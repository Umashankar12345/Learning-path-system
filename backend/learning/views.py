from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Skill, Resource, LearningPath, PathItem
from .serializers import (
    UserSerializer,
    SignupSerializer,
    SkillSerializer,
    ResourceSerializer,
    LearningPathSerializer,
    LearningPathDetailSerializer,
    PathItemSerializer,
)
from .permissions import IsOwner
from .recommender import PathRecommender


class SignupView(generics.CreateAPIView):
    """
    Register a new learner account and return JWT credentials.
    """
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

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


class MeView(views.APIView):
    """
    Return current authenticated user profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class SkillListView(generics.ListAPIView):
    """
    List all available skill goals (e.g., Data Science, Full-Stack Development).
    """
    queryset = Skill.objects.all().prefetch_related("resources")
    serializer_class = SkillSerializer
    permission_classes = [AllowAny]


class ResourceListView(generics.ListAPIView):
    """
    List and filter learning resources.
    """
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


class LearningPathListCreateView(generics.ListCreateAPIView):
    """
    List user's active paths or generate a new path from a skill.
    """
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


class LearningPathDetailView(generics.RetrieveDestroyAPIView):
    """
    Retrieve full path details including all ordered PathItems.
    """
    serializer_class = LearningPathDetailSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return (
            LearningPath.objects.filter(user=self.request.user)
            .select_related("skill")
            .prefetch_related("items__resource")
        )


class MarkItemCompleteView(views.APIView):
    """
    POST to toggle completion state of a PathItem (saves completed_at).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        item = get_object_or_404(PathItem, pk=pk, path__user=request.user)

        # Toggle or force completed based on payload
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

        return Response(PathItemSerializer(item).data, status=status.HTTP_200_OK)


class RateItemView(views.APIView):
    """
    POST to set a 1-5 rating on a PathItem.
    """
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


class DashboardStatsView(views.APIView):
    """
    Dashboard metrics queried live from the database:
    - Active paths count
    - Completed vs Total items
    - Overall completion percentage
    - Total hours learned
    - Day streak
    - Progress bars per path
    - Next recommended item
    - Weekly hours activity (Chart.js / visual)
    """
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

        # If user hasn't completed anything today, check if yesterday had completions
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
