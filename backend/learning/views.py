import os
import json
import logging
import re
import requests
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum, Count, Q
from django.db import transaction
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from .models import (
    AssessmentAttempt,
    CodingAttempt,
    CodingChallenge,
    CodeSubmission,
    PlacementQuestion,
    Skill,
    Resource,
    LearningPath,
    PathItem,
    ProjectSubmission,
)
from .serializers import (
    ArenaSubmissionResultSerializer,
    ArenaDailyChallengeSerializer,
    CodeExecutionRequestSerializer,
    CodeSubmissionSerializer,
    DashboardStatsSerializer,
    ErrorResponseSerializer,
    GitHubPublicRepositorySerializer,
    GoogleAuthRequestSerializer,
    GoogleAuthResponseSerializer,
    ItemRatingRequestSerializer,
    LeaderboardEntrySerializer,
    LearningPathCreateRequestSerializer,
    PathCompletionRequestSerializer,
    PlacementQuestionSerializer,
    PlacementResultSerializer,
    PlacementSubmissionSerializer,
    ReferenceSolutionSerializer,
    SignupResponseSerializer,
    SkillRadarPointSerializer,
    CodingAttemptSerializer,
    CodingAttemptStartSerializer,
    CodingAttemptResultSerializer,
    CodingChallengeSerializer,
    UserSerializer,
    SignupSerializer,
    SkillSerializer,
    ResourceSerializer,
    LearningPathSerializer,
    LearningPathDetailSerializer,
    PathItemSerializer,
    ProjectSubmissionSerializer,
)
from .permissions import IsOwner
from .recommender import PathRecommender
from .notifications import send_welcome_email, send_streak_email, send_completion_email
from .certificates import generate_completion_certificate
from .judge import JudgeConfigurationError, JudgeServiceError, run_test_case

logger = logging.getLogger(__name__)


def run_challenge_test_cases(challenge, source_code):
    test_cases = list(challenge.test_cases.all())
    if not test_cases or len(test_cases) > 10:
        raise JudgeConfigurationError(
            "This challenge does not have a valid number of configured test cases."
        )

    results = []
    total_execution_time = 0.0
    for case in test_cases:
        result = run_test_case(
            source_code=source_code,
            language_id=challenge.language_id,
            stdin=case.stdin,
            expected_output=case.expected_output,
        )
        total_execution_time += float(result.get("time") or 0)
        case_result = {
            "order": case.order,
            "is_sample": case.is_sample,
            "passed": result["status"] == "accepted",
            "status": result["status"],
        }
        if case.is_sample and result.get("diagnostic"):
            case_result["diagnostic"] = result["diagnostic"]
        results.append(case_result)

    passed_count = sum(result["passed"] for result in results)
    if passed_count == len(results):
        final_status = CodingAttempt.Status.ACCEPTED
    elif any(result["status"] == "time_limit" for result in results):
        final_status = CodingAttempt.Status.TIME_LIMIT
    elif any(result["status"] == "compile_error" for result in results):
        final_status = CodingAttempt.Status.COMPILE_ERROR
    elif any(result["status"] == "runtime_error" for result in results):
        final_status = CodingAttempt.Status.RUNTIME_ERROR
    elif passed_count:
        final_status = CodingAttempt.Status.PARTIAL
    else:
        final_status = CodingAttempt.Status.WRONG_ANSWER

    return {
        "results": results,
        "passed_count": passed_count,
        "total_count": len(results),
        "status": final_status,
        "runtime_ms": round(total_execution_time * 1000),
    }


def create_code_submission(user, challenge, source_code, language):
    result = run_challenge_test_cases(challenge, source_code)
    submission = CodeSubmission.objects.create(
        user=user,
        challenge=challenge,
        language=language,
        source_code=source_code,
        passed_count=result["passed_count"],
        total_count=result["total_count"],
        status=result["status"],
        runtime_ms=result["runtime_ms"],
    )
    return submission, result["results"]


def get_daily_challenge(today):
    scheduled = CodingChallenge.objects.filter(
        is_active=True,
        is_daily_challenge=True,
        challenge_date=today,
    ).order_by("id")
    if scheduled.exists():
        return scheduled.first()

    candidates = list(
        CodingChallenge.objects.filter(
            is_active=True,
            is_daily_challenge=True,
            challenge_date__isnull=True,
        ).order_by("id")
    )
    if not candidates:
        candidates = list(CodingChallenge.objects.filter(is_active=True).order_by("id"))
    if not candidates:
        return None
    return candidates[today.toordinal() % len(candidates)]


def get_coding_streak(user, today):
    completed_dates = CodeSubmission.objects.filter(
        user=user,
        status=CodeSubmission.Status.ACCEPTED,
    ).dates("created_at", "day", order="DESC")
    if not completed_dates:
        return 0

    latest = completed_dates[0]
    if latest == today:
        streak = 1
        current_date = today - timedelta(days=1)
    elif latest == today - timedelta(days=1):
        streak = 1
        current_date = today - timedelta(days=2)
    else:
        return 0

    for completed_date in completed_dates[1:]:
        if completed_date == current_date:
            streak += 1
            current_date -= timedelta(days=1)
        elif completed_date < current_date:
            break
    return streak


@extend_schema(
    summary="Register a new learner",
    description="Creates a new learner account, sends a welcome email, and returns JWT tokens.",
    request=SignupSerializer,
    responses={201: SignupResponseSerializer},
    tags=["Authentication"],
)
class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Send welcome email notification
        send_welcome_email(user)

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "token": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                "message": "User registered successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    summary="Sign in or register with Google OAuth",
    description="Authenticates via Google credential/token, auto-provisions account if needed, and returns JWT credentials.",
    request=GoogleAuthRequestSerializer,
    responses={
        200: GoogleAuthResponseSerializer,
        400: ErrorResponseSerializer,
        503: ErrorResponseSerializer,
    },
    tags=["Authentication"],
)
class GoogleAuthView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("credential") or request.data.get("id_token")
        email = request.data.get("email")
        name = request.data.get("name")

        if not token:
            return Response(
                {"error": "A verified Google credential is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_email = email
        user_name = name or ""

        client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        if not client_id or "your-google-web-client-id" in client_id:
            return Response(
                {"error": "Google sign-in is not configured. Set GOOGLE_CLIENT_ID."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            from google.oauth2 import id_token
            from google.auth.transport import requests as google_requests

            id_info = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                client_id,
            )
            user_email = id_info.get("email")
            user_name = id_info.get("name", user_name)
            if not user_email or not id_info.get("email_verified", False):
                return Response(
                    {"error": "Google account must have a verified email address."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"error": f"Invalid Google credential: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        username = user_email.split("@")[0]
        user, created = User.objects.get_or_create(
            email=user_email,
            defaults={
                "username": username,
                "first_name": user_name.split(" ")[0] if user_name else username,
                "last_name": " ".join(user_name.split(" ")[1:]) if " " in user_name else "",
            },
        )

        if created:
            user.set_unusable_password()
            user.save()
            send_welcome_email(user)

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "token": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                "created": created,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    summary="Get current user profile",
    description="Returns the profile information of the currently authenticated user.",
    tags=["Authentication"],
    responses=UserSerializer,
)
class MeView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


@extend_schema(
    summary="List available skill goals",
    description="Retrieves all learning skill goals available for enrollment.",
    tags=["Catalog"],
    responses=SkillSerializer(many=True),
)
class SkillListView(generics.ListAPIView):
    queryset = Skill.objects.all().prefetch_related("resources")
    serializer_class = SkillSerializer
    permission_classes = [AllowAny]


@extend_schema(
    summary="Get placement assessment questions for a skill",
    description="Returns ten active multiple-choice questions without exposing their correct answers.",
    responses={
        200: PlacementQuestionSerializer(many=True),
        503: ErrorResponseSerializer,
    },
    tags=["Placement Assessment"],
)
class PlacementQuizView(generics.ListAPIView):
    serializer_class = PlacementQuestionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        skill = get_object_or_404(Skill, pk=self.kwargs["pk"])
        questions = PlacementQuestion.objects.filter(
            skill=skill,
            is_active=True,
        ).order_by("difficulty", "id")[:10]
        if questions.count() < 10:
            return PlacementQuestion.objects.none()
        return questions

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"error": "This skill does not have ten active placement questions yet."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return super().list(request, *args, **kwargs)


@extend_schema(
    summary="Grade a placement assessment and create a personalized path",
    request=PlacementSubmissionSerializer,
    responses={
        201: PlacementResultSerializer,
        400: ErrorResponseSerializer,
        503: ErrorResponseSerializer,
    },
    tags=["Placement Assessment"],
)
class PlacementSubmitView(views.APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        skill = get_object_or_404(Skill, pk=pk)
        serializer = PlacementSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        questions = list(
            PlacementQuestion.objects.filter(skill=skill, is_active=True)
            .order_by("difficulty", "id")[:10]
        )
        if len(questions) != 10:
            return Response(
                {"error": "This skill does not have ten active placement questions yet."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        submitted_answers = serializer.validated_data["answers"]
        answer_by_id = {
            answer["question_id"]: answer["selected_option"]
            for answer in submitted_answers
        }
        expected_ids = {question.id for question in questions}
        if (
            len(answer_by_id) != len(submitted_answers)
            or set(answer_by_id) != expected_ids
        ):
            return Response(
                {"error": "Submit exactly one answer for each placement question."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        correct_answers = sum(
            answer_by_id[question.id] == question.correct_option
            for question in questions
        )
        score = round(correct_answers * 100 / len(questions))
        breakdown = []
        passed_level = 1
        for difficulty in PlacementQuestion.Difficulty.values:
            level_questions = [
                question for question in questions
                if question.difficulty == difficulty
            ]
            level_correct = sum(
                answer_by_id[question.id] == question.correct_option
                for question in level_questions
            )
            total = len(level_questions)
            accuracy = round(level_correct * 100 / total) if total else 0
            if accuracy >= 60 and difficulty == passed_level:
                passed_level += 1
            breakdown.append({
                "difficulty": difficulty,
                "label": PlacementQuestion.Difficulty(difficulty).label,
                "correct": level_correct,
                "total": total,
                "accuracy": accuracy,
                "status": (
                    "strong" if accuracy >= 80
                    else "developing" if accuracy >= 60
                    else "needs_work"
                ),
            })

        recommended_level = min(passed_level, 3)
        path, _ = LearningPath.objects.get_or_create(
            user=request.user,
            skill=skill,
        )
        PathRecommender.generate_path_items(path)
        PathItem.objects.filter(
            path=path,
            resource__difficulty__lt=recommended_level,
            completed=False,
        ).update(
            completed=True,
            completed_at=timezone.now(),
        )
        attempt = AssessmentAttempt.objects.create(
            user=request.user,
            skill=skill,
            score=score,
            correct_answers=correct_answers,
            total_questions=len(questions),
            recommended_level=recommended_level,
            skill_gap_breakdown=breakdown,
        )

        result = {
            "id": attempt.id,
            "score": attempt.score,
            "correct_answers": attempt.correct_answers,
            "total_questions": attempt.total_questions,
            "recommended_level": attempt.recommended_level,
            "recommended_level_label": attempt.get_recommended_level_display(),
            "skill_gap_breakdown": attempt.skill_gap_breakdown,
            "path_id": path.id,
            "created_at": attempt.created_at,
        }
        return Response(
            PlacementResultSerializer(result).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    summary="Filter resources",
    description="Browse learning resources with optional filtering by skill, difficulty level, or resource type.",
    tags=["Catalog"],
    parameters=[
        OpenApiParameter("skill", OpenApiTypes.INT, description="Filter by Skill ID"),
        OpenApiParameter("difficulty", OpenApiTypes.INT, description="Filter by difficulty (1, 2, 3)"),
        OpenApiParameter("type", OpenApiTypes.STR, description="Filter by resource type (video, article, course, project)"),
    ],
    responses=ResourceSerializer(many=True),
)
class ResourceListView(generics.ListAPIView):
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Resource.objects.all().select_related("skill")
        skill_id = self.request.query_params.get("skill")
        difficulty = self.request.query_params.get("difficulty")
        resource_type = self.request.query_params.get("type")

        if skill_id:
            queryset = queryset.filter(skill_id=skill_id)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)
        return queryset


@extend_schema_view(
    get=extend_schema(
        summary="List the current learner's paths",
        responses=LearningPathSerializer(many=True),
        request=None,
    ),
    post=extend_schema(
        summary="Create or retrieve a learning path",
        description="Generate an ordered path from a skill, or return the existing path.",
        request=LearningPathCreateRequestSerializer,
        responses={
            200: LearningPathDetailSerializer,
            201: LearningPathDetailSerializer,
        },
    ),
)
@extend_schema(tags=["Learning Paths"])
class LearningPathListCreateView(generics.ListCreateAPIView):
    serializer_class = LearningPathSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            LearningPath.objects.filter(user=self.request.user)
            .select_related("skill")
            .prefetch_related("items__resource")
        )

    def create(self, request, *args, **kwargs):
        skill_id = request.data.get("skill_id")
        if not skill_id:
            return Response(
                {"error": "skill_id is required to create a learning path."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        skill = get_object_or_404(Skill, id=skill_id)

        # Retrieve existing or create new path
        learning_path, created = LearningPath.objects.get_or_create(
            user=request.user,
            skill=skill,
        )

        # Generate ordered PathItem rows via Recommender
        PathRecommender.generate_path_items(learning_path)

        serializer = LearningPathDetailSerializer(learning_path)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


@extend_schema_view(
    get=extend_schema(
        summary="Get learning path details",
        description="Retrieve all difficulty-ranked milestones and their completion statuses.",
        responses=LearningPathDetailSerializer,
        request=None,
    ),
    delete=extend_schema(
        summary="Delete a learning path",
        responses={204: OpenApiResponse(description="The path was deleted.")},
        request=None,
    ),
)
@extend_schema(tags=["Learning Paths"])
class LearningPathDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = LearningPathDetailSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return (
            LearningPath.objects.filter(user=self.request.user)
            .select_related("skill")
            .prefetch_related("items__resource")
        )


@extend_schema(
    summary="Mark milestone complete or incomplete",
    description="Toggles the completion state of a milestone, logs the timestamp, and triggers celebratory notifications.",
    request=PathCompletionRequestSerializer,
    responses={
        200: PathItemSerializer,
        400: ErrorResponseSerializer,
    },
    tags=["Milestones"],
)
class MarkItemCompleteView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        item = get_object_or_404(PathItem, pk=pk, path__user=request.user)
        path = item.path

        # Toggle or set completed based on action
        action = request.data.get("action", "toggle")
        will_complete = action == "complete" or (
            action != "uncomplete" and not item.completed
        )
        if (
            will_complete
            and item.resource.coding_challenge_id
            and not CodeSubmission.objects.filter(
                user=request.user,
                challenge_id=item.resource.coding_challenge_id,
                status=CodeSubmission.Status.ACCEPTED,
            ).exists()
        ):
            return Response(
                {"error": "Pass the linked coding challenge before completing this module."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if action == "uncomplete":
            item.mark_incomplete()
        elif action == "complete":
            item.mark_complete()
        else:
            if item.completed:
                item.mark_incomplete()
            else:
                item.mark_complete()

        # Check if 100% path completed -> trigger certificate email
        if item.completed and path.progress_percentage == 100:
            send_completion_email(request.user, path)

        return Response(PathItemSerializer(item).data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Rate a learning milestone",
    description="Submit an integer rating from 1 to 5 stars for a specific learning module.",
    request=ItemRatingRequestSerializer,
    responses={
        200: PathItemSerializer,
        400: ErrorResponseSerializer,
    },
    tags=["Milestones"],
)
class RateItemView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        item = get_object_or_404(PathItem, pk=pk, path__user=request.user)
        rating = request.data.get("rating")

        if rating is None or not (1 <= int(rating) <= 5):
            return Response(
                {"error": "Rating must be an integer between 1 and 5."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item.rating = int(rating)
        item.save(update_fields=["rating"])
        return Response(PathItemSerializer(item).data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Submit or update a GitHub project",
    description="Learners submit a GitHub repository for a project milestone. Instructors review it in Django Admin.",
    request=ProjectSubmissionSerializer,
    responses={
        200: ProjectSubmissionSerializer,
        201: ProjectSubmissionSerializer,
        400: ErrorResponseSerializer,
    },
    tags=["Project Reviews"],
)
class ProjectSubmissionView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        item = get_object_or_404(
            PathItem.objects.select_related("resource", "path"),
            pk=pk,
            path__user=request.user,
        )
        if item.resource.resource_type != "project":
            return Response(
                {"error": "GitHub submissions are only available for project milestones."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ProjectSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submission, created = ProjectSubmission.objects.get_or_create(item=item)
        submission.github_url = serializer.validated_data["github_url"]
        submission.reflection = serializer.validated_data.get("reflection", "")
        submission.status = ProjectSubmission.ReviewStatus.PENDING
        submission.teacher_feedback = ""
        submission.reviewed_at = None
        submission.reviewed_by = None
        submission.save()
        return Response(
            ProjectSubmissionSerializer(submission).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


@extend_schema(
    summary="List active coding challenges",
    responses=CodingChallengeSerializer(many=True),
    tags=["Coding Challenges"],
)
class CodingChallengeListView(generics.ListAPIView):
    serializer_class = CodingChallengeSerializer
    permission_classes = [AllowAny]
    queryset = CodingChallenge.objects.filter(is_active=True).prefetch_related("test_cases")


@extend_schema(
    summary="Get challenge details and sample cases",
    responses=CodingChallengeSerializer,
    tags=["Coding Challenges"],
)
class CodingChallengeDetailView(generics.RetrieveAPIView):
    serializer_class = CodingChallengeSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"
    queryset = CodingChallenge.objects.filter(is_active=True).prefetch_related("test_cases")


@extend_schema(
    summary="Filter coding arena problems",
    parameters=[
        OpenApiParameter("difficulty", OpenApiTypes.STR, description="Filter by easy, medium, or hard."),
        OpenApiParameter("topic", OpenApiTypes.STR, description="Filter by a problem topic tag."),
    ],
    responses=CodingChallengeSerializer(many=True),
    tags=["Coding Arena"],
)
class ArenaProblemListView(generics.ListAPIView):
    serializer_class = CodingChallengeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = CodingChallenge.objects.filter(is_active=True).prefetch_related(
            "test_cases"
        )
        difficulty = self.request.query_params.get("difficulty")
        topic = self.request.query_params.get("topic", "").strip().casefold()
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if topic:
            matching_ids = [
                challenge.id
                for challenge in queryset
                if any(
                    isinstance(tag, str) and tag.casefold() == topic
                    for tag in challenge.topic_tags
                )
            ]
            queryset = queryset.filter(id__in=matching_ids)
        return queryset


@extend_schema(
    summary="Browse a GitHub user's public repositories",
    description=(
        "Returns up to 100 public repositories for a GitHub username. "
        "This endpoint does not access private repositories or require OAuth."
    ),
    responses={
        200: GitHubPublicRepositorySerializer(many=True),
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
        429: OpenApiResponse(description="Rate limit exceeded; retry after the indicated delay."),
        502: ErrorResponseSerializer,
        503: ErrorResponseSerializer,
    },
    tags=["GitHub"],
)
class GitHubPublicRepositoryListView(views.APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "github_public"

    def get(self, request, username):
        if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", username):
            return Response(
                {"error": "Enter a valid GitHub username."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            response = requests.get(
                f"https://api.github.com/users/{username}/repos",
                params={"sort": "updated", "per_page": 100},
                headers={
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                    "User-Agent": "LearningPath.ai",
                },
                timeout=8,
            )
        except requests.RequestException:
            logger.exception("GitHub repository lookup failed for username %s", username)
            return Response(
                {"error": "GitHub's public repository service is temporarily unavailable."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if response.status_code == 404:
            return Response(
                {"error": "GitHub user was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if response.status_code == 403:
            return Response(
                {"error": "GitHub's public API rate limit has been reached. Try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        if response.status_code >= 500:
            return Response(
                {"error": "GitHub's public repository service is temporarily unavailable."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        if response.status_code != 200:
            logger.warning(
                "GitHub repository lookup returned status %s for username %s",
                response.status_code,
                username,
            )
            return Response(
                {"error": "GitHub could not complete the repository lookup."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        try:
            repositories = response.json()
        except ValueError:
            logger.warning("GitHub returned invalid JSON for username %s", username)
            return Response(
                {"error": "GitHub returned an invalid repository response."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        if not isinstance(repositories, list):
            return Response(
                {"error": "GitHub returned an invalid repository response."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        public_repositories = [
            repository
            for repository in repositories
            if isinstance(repository, dict) and repository.get("private") is False
        ]
        serializer = GitHubPublicRepositorySerializer(
            data=public_repositories,
            many=True,
        )
        if not serializer.is_valid():
            logger.warning("GitHub returned an unexpected repository payload")
            return Response(
                {"error": "GitHub returned an invalid repository response."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(serializer.data)


@extend_schema(
    summary="Submit code to an arena problem",
    request=CodeExecutionRequestSerializer,
    responses={
        201: ArenaSubmissionResultSerializer,
        400: OpenApiResponse(description="The submission payload is invalid."),
        502: ErrorResponseSerializer,
        503: ErrorResponseSerializer,
    },
    tags=["Coding Arena"],
)
class ArenaProblemSubmitView(views.APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "coding_challenge"

    def post(self, request, pk):
        challenge = get_object_or_404(CodingChallenge, pk=pk, is_active=True)
        if not getattr(settings, "JUDGE0_API_URL", "").strip():
            return Response(
                {"error": "Hosted code judging is not configured. Set JUDGE0_API_URL and credentials."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        serializer = CodeExecutionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            submission, test_results = create_code_submission(
                request.user,
                challenge,
                serializer.validated_data["source_code"],
                serializer.validated_data["language"],
            )
        except JudgeConfigurationError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except JudgeServiceError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {
                **CodeSubmissionSerializer(submission).data,
                "test_results": test_results,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    summary="List the current learner's coding submissions",
    responses=CodeSubmissionSerializer(many=True),
    tags=["Coding Arena"],
)
class ArenaSubmissionHistoryView(generics.ListAPIView):
    serializer_class = CodeSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CodeSubmission.objects.filter(user=self.request.user).select_related(
            "challenge"
        )


@extend_schema(
    summary="Unlock a problem's reference solution after an attempt",
    responses={
        200: ReferenceSolutionSerializer,
        403: ErrorResponseSerializer,
        503: ErrorResponseSerializer,
    },
    tags=["Coding Arena"],
)
class ArenaProblemSolutionView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        challenge = get_object_or_404(CodingChallenge, pk=pk, is_active=True)
        has_attempted = CodeSubmission.objects.filter(
            user=request.user,
            challenge=challenge,
        ).exists()
        if not has_attempted:
            return Response(
                {"error": "Submit at least one solution attempt to unlock this reference solution."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if not challenge.reference_solution.strip():
            return Response(
                {"error": "A reference solution has not been configured for this problem."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response({
            "challenge_id": challenge.id,
            "challenge_title": challenge.title,
            "language": "python3",
            "reference_solution": challenge.reference_solution,
        })


@extend_schema(
    summary="Get today's coding challenge and coding streak",
    responses={
        200: ArenaDailyChallengeSerializer,
        404: ErrorResponseSerializer,
    },
    tags=["Coding Arena"],
)
class ArenaDailyChallengeView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        challenge = get_daily_challenge(today)
        if challenge is None:
            return Response(
                {"error": "No active coding challenge is available."},
                status=status.HTTP_404_NOT_FOUND,
            )
        completed_today = CodeSubmission.objects.filter(
            user=request.user,
            challenge=challenge,
            status=CodeSubmission.Status.ACCEPTED,
            created_at__date=today,
        ).exists()
        return Response({
            "challenge": CodingChallengeSerializer(challenge).data,
            "coding_streak": get_coding_streak(request.user, today),
            "completed_today": completed_today,
        })


@extend_schema(
    summary="Start a timed coding attempt",
    request=None,
    responses=CodingAttemptStartSerializer,
    tags=["Coding Challenges"],
)
class CodingChallengeStartView(views.APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "coding_challenge"

    @extend_schema(request=None, responses={201: CodingAttemptStartSerializer})
    def post(self, request, pk):
        challenge = get_object_or_404(CodingChallenge, pk=pk, is_active=True)
        if not getattr(settings, "JUDGE0_API_URL", "").strip():
            return Response(
                {"error": "Hosted code judging is not configured. Set JUDGE0_API_URL and credentials."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        attempt = CodingAttempt.objects.create(user=request.user, challenge=challenge)
        return Response(
            CodingAttemptStartSerializer(attempt).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    summary="Submit code to hosted Judge0 test runner",
    request=CodeExecutionRequestSerializer,
    responses=CodingAttemptResultSerializer,
    tags=["Coding Challenges"],
)
class CodingChallengeSubmitView(views.APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "coding_challenge"

    @extend_schema(
        request=CodeExecutionRequestSerializer,
        responses=CodingAttemptResultSerializer,
    )
    def post(self, request, pk):
        attempt = get_object_or_404(
            CodingAttempt.objects.select_related("challenge"),
            pk=pk,
            user=request.user,
        )
        if attempt.status != CodingAttempt.Status.IN_PROGRESS:
            return Response(
                {"error": "This attempt has already been submitted."},
                status=status.HTTP_409_CONFLICT,
            )
        expires_at = attempt.started_at + timedelta(
            minutes=attempt.challenge.duration_minutes
        )
        if timezone.now() >= expires_at:
            return Response(
                {"error": "The challenge timer has expired. Start a new attempt."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CodeExecutionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["source_code"]
        try:
            submission, results = create_code_submission(
                request.user,
                attempt.challenge,
                code,
                serializer.validated_data["language"],
            )
        except JudgeConfigurationError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except JudgeServiceError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        attempt.source_code = code
        attempt.status = submission.status
        attempt.submitted_at = timezone.now()
        attempt.passed_test_cases = submission.passed_count
        attempt.total_test_cases = submission.total_count
        attempt.execution_time_ms = submission.runtime_ms
        attempt.save(
            update_fields=[
                "source_code",
                "status",
                "submitted_at",
                "passed_test_cases",
                "total_test_cases",
                "execution_time_ms",
            ]
        )
        return Response(
            {
                **CodingAttemptSerializer(attempt).data,
                "test_results": results,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    summary="Download PDF Certificate of Completion",
    description="Generates an official personalized PDF Certificate of Completion with verification ID.",
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.BINARY,
            description="PDF certificate file.",
        ),
    },
    tags=["Certificates"],
)
class CertificateDownloadView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        path = get_object_or_404(LearningPath, pk=pk, user=request.user)
        pdf_buffer = generate_completion_certificate(path)

        filename = f"Certificate_{path.skill.name.replace(' ', '_')}.pdf"
        response = HttpResponse(pdf_buffer.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


@extend_schema(
    summary="Community Leaderboard",
    description="Live rankings of active learners by completed study hours and milestones (hides admin and zero-progress accounts).",
    responses=LeaderboardEntrySerializer(many=True),
    tags=["Community"],
)
class LeaderboardView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Rule 1: Hide staff / admin accounts
        # Rule 2: Only include users with real completed progress
        users = User.objects.filter(is_active=True, is_staff=False, is_superuser=False)

        leaderboard = []
        for u in users:
            items = PathItem.objects.filter(path__user=u, completed=True)
            completed_count = items.count()

            # Rule 2: Hide users with zero completed items
            if completed_count == 0:
                continue

            duration_sum = items.aggregate(total=Sum("resource__duration_minutes"))["total"] or 0
            hours = round(duration_sum / 60.0, 1)

            # Dynamic badges
            badges = []
            if completed_count >= 1:
                badges.append({"id": "first_step", "name": "First Milestone", "icon": "🥉"})
            if completed_count >= 3:
                badges.append({"id": "on_a_roll", "name": "Consistent Learner", "icon": "🥈"})
            if completed_count >= 5:
                badges.append({"id": "mastery", "name": "Skill Scholar", "icon": "🥇"})
            if hours >= 3.0:
                badges.append({"id": "deep_diver", "name": "Deep Diver", "icon": "⚡"})
            if LearningPath.objects.filter(user=u).filter(~Q(items__completed=False)).exists() and completed_count > 0:
                badges.append({"id": "champion", "name": "Track Champion", "icon": "🏆"})

            leaderboard.append({
                "id": u.id,
                "username": u.username,
                "name": u.get_full_name() or u.username,
                "completed_count": completed_count,
                "hours_learned": hours,
                "badges": badges,
            })

        # Sort by hours_learned descending, then completed_count
        leaderboard.sort(key=lambda x: (x["hours_learned"], x["completed_count"]), reverse=True)

        # Add 1-based rank
        for idx, entry in enumerate(leaderboard, start=1):
            entry["rank"] = idx

        return Response(leaderboard)


@extend_schema(
    summary="Personalized Dashboard Metrics",
    description="Calculates live analytics: active paths, completion rate, hours learned, day streak, and next recommendation.",
    responses=DashboardStatsSerializer,
    tags=["Dashboard"],
)
class DashboardStatsView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        paths = (
            LearningPath.objects.filter(user=user)
            .select_related("skill")
            .prefetch_related("items__resource")
        )

        active_paths_count = paths.count()
        user_items = PathItem.objects.filter(path__user=user)
        total_items = user_items.count()
        completed_items = user_items.filter(completed=True).count()
        overall_progress = round((completed_items / total_items * 100), 1) if total_items > 0 else 0

        # Hours learned from completed items duration
        completed_duration = (
            user_items.filter(completed=True)
            .aggregate(total=Sum("resource__duration_minutes"))["total"] or 0
        )
        total_hours_learned = round(completed_duration / 60.0, 1)

        # Day streak calculation
        completed_dates = (
            user_items.filter(completed=True, completed_at__isnull=False)
            .dates("completed_at", "day", order="DESC")
        )
        today = timezone.now().date()
        streak = 0
        current_check = today

        if completed_dates:
            latest_date = completed_dates[0]
            if latest_date == today:
                streak = 1
                current_check = today - timedelta(days=1)
            elif latest_date == today - timedelta(days=1):
                streak = 1
                current_check = today - timedelta(days=2)
            else:
                streak = 0

            if streak > 0:
                for d in completed_dates[1:]:
                    if d == current_check:
                        streak += 1
                        current_check = current_check - timedelta(days=1)
                    elif d < current_check:
                        break

        # Check for milestone streak email
        send_streak_email(user, streak)

        # Next recommended resource
        next_item = PathRecommender.get_next_recommended_resource(user)
        next_item_data = PathItemSerializer(next_item).data if next_item else None

        # Weekly hours chart data (last 7 days)
        weekly_activity = []
        for i in range(6, -1, -1):
            day_date = today - timedelta(days=i)
            day_duration = (
                user_items.filter(
                    completed=True,
                    completed_at__date=day_date
                ).aggregate(total=Sum("resource__duration_minutes"))["total"] or 0
            )
            weekly_activity.append({
                "date": day_date.strftime("%Y-%m-%d"),
                "day": day_date.strftime("%a"),
                "hours": round(day_duration / 60.0, 2),
                "minutes": day_duration,
            })

        # Paths progress data
        paths_data = LearningPathSerializer(paths, many=True).data

        return Response({
            "active_paths_count": active_paths_count,
            "total_items": total_items,
            "completed_items": completed_items,
            "overall_progress": overall_progress,
            "total_hours_learned": total_hours_learned,
            "day_streak": streak,
            "next_recommended_item": next_item_data,
            "weekly_activity": weekly_activity,
            "paths": paths_data,
        })


@extend_schema(
    summary="Get normalized skill radar analytics for the current learner",
    description=(
        "Returns a 0-100 topic score combining module completion (50%), "
        "relative study hours (25%), and the latest placement assessment (25%)."
    ),
    responses=SkillRadarPointSerializer(many=True),
    tags=["Dashboard"],
)
class SkillRadarView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        paths = list(
            LearningPath.objects.filter(user=request.user)
            .select_related("skill")
            .prefetch_related("items__resource")
        )
        topic_data = []
        for path in paths:
            items = list(path.items.all())
            completed_items = [item for item in items if item.completed]
            minutes = sum(
                item.resource.duration_minutes
                for item in completed_items
            )
            latest_assessment = AssessmentAttempt.objects.filter(
                user=request.user,
                skill=path.skill,
            ).first()
            topic_data.append({
                "topic": path.skill.name,
                "completed_modules": len(completed_items),
                "total_modules": len(items),
                "study_hours": round(minutes / 60, 1),
                "quiz_score": latest_assessment.score if latest_assessment else 0,
            })

        max_hours = max(
            (point["study_hours"] for point in topic_data),
            default=0,
        )
        for point in topic_data:
            completion_score = (
                point["completed_modules"] * 100 / point["total_modules"]
                if point["total_modules"] else 0
            )
            hours_score = (
                point["study_hours"] * 100 / max_hours
                if max_hours else 0
            )
            point["score"] = round(
                completion_score * 0.5
                + hours_score * 0.25
                + point["quiz_score"] * 0.25
            )
        return Response(SkillRadarPointSerializer(topic_data, many=True).data)
