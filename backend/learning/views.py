import os
import json
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum, Count, Q
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .models import (
    CodingAttempt,
    CodingChallenge,
    Skill,
    Resource,
    LearningPath,
    PathItem,
    ProjectSubmission,
)
from .serializers import (
    CodeSubmissionSerializer,
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


@extend_schema(
    summary="Register a new learner",
    description="Creates a new learner account, sends a welcome email, and returns JWT tokens.",
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


@extend_schema(
    summary="List or create learning paths",
    description="List active learning paths for the user or generate an ordered path from a skill.",
    tags=["Learning Paths"],
)
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


@extend_schema(
    summary="Get learning path details",
    description="Retrieve the complete learning path with all difficulty-ranked milestones and completion statuses.",
    tags=["Learning Paths"],
    responses=LearningPathDetailSerializer,
)
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
    tags=["Milestones"],
    responses=PathItemSerializer,
)
class MarkItemCompleteView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        item = get_object_or_404(PathItem, pk=pk, path__user=request.user)
        path = item.path

        # Toggle or set completed based on action
        action = request.data.get("action", "toggle")
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
    tags=["Milestones"],
    responses=PathItemSerializer,
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
    responses=ProjectSubmissionSerializer,
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
    request=CodeSubmissionSerializer,
    responses=CodingAttemptResultSerializer,
    tags=["Coding Challenges"],
)
class CodingChallengeSubmitView(views.APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "coding_challenge"

    @extend_schema(
        request=CodeSubmissionSerializer,
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

        serializer = CodeSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        test_cases = list(attempt.challenge.test_cases.all())
        if not test_cases or len(test_cases) > 10:
            return Response(
                {"error": "This challenge does not have a valid number of configured test cases."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        code = serializer.validated_data["source_code"]
        results = []
        total_execution_time = 0.0
        try:
            for case in test_cases:
                result = run_test_case(
                    source_code=code,
                    language_id=attempt.challenge.language_id,
                    stdin=case.stdin,
                    expected_output=case.expected_output,
                )
                passed = result["status"] == "accepted"
                total_execution_time += float(result.get("time") or 0)
                case_result = {
                    "order": case.order,
                    "is_sample": case.is_sample,
                    "passed": passed,
                    "status": result["status"],
                }
                if case.is_sample and result.get("diagnostic"):
                    case_result["diagnostic"] = result["diagnostic"]
                results.append(case_result)
        except JudgeConfigurationError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except JudgeServiceError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

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

        attempt.source_code = code
        attempt.status = final_status
        attempt.submitted_at = timezone.now()
        attempt.passed_test_cases = passed_count
        attempt.total_test_cases = len(results)
        attempt.execution_time_ms = round(total_execution_time * 1000)
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
