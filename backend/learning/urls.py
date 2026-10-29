from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    SignupView,
    MeView,
    SkillListView,
    ResourceListView,
    LearningPathListCreateView,
    LearningPathDetailView,
    MarkItemCompleteView,
    RateItemView,
    DashboardStatsView,
)

urlpatterns = [
    # Auth endpoints
    path("auth/signup/", SignupView.as_view(), name="signup"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", MeView.as_view(), name="me"),

    # Catalog endpoints
    path("skills/", SkillListView.as_view(), name="skill-list"),
    path("resources/", ResourceListView.as_view(), name="resource-list"),

    # Learning Path endpoints
    path("paths/", LearningPathListCreateView.as_view(), name="path-list-create"),
    path("paths/<int:pk>/", LearningPathDetailView.as_view(), name="path-detail"),

    # Item actions
    path("items/<int:pk>/complete/", MarkItemCompleteView.as_view(), name="item-complete"),
    path("items/<int:pk>/rate/", RateItemView.as_view(), name="item-rate"),

    # Dashboard analytics
    path("dashboard/stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
]
