from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    SignupView,
    GoogleAuthView,
    MeView,
    SkillListView,
    ResourceListView,
    GitHubPublicRepositoryListView,
    LearningPathListCreateView,
    LearningPathDetailView,
    MarkItemCompleteView,
    RateItemView,
    ProjectSubmissionView,
    CodingChallengeListView,
    CodingChallengeDetailView,
    CodingChallengeStartView,
    CodingChallengeSubmitView,
    ArenaProblemListView,
    ArenaProblemSubmitView,
    ArenaSubmissionHistoryView,
    ArenaProblemSolutionView,
    ArenaDailyChallengeView,
    PlacementQuizView,
    PlacementSubmitView,
    CertificateDownloadView,
    LeaderboardView,
    DashboardStatsView,
    SkillRadarView,
)

urlpatterns = [
    # Auth endpoints
    path("auth/signup/", SignupView.as_view(), name="signup"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/google/", GoogleAuthView.as_view(), name="google-auth"),
    path("auth/me/", MeView.as_view(), name="me"),

    # Catalog & Leaderboard endpoints
    path("skills/", SkillListView.as_view(), name="skill-list"),
    path("resources/", ResourceListView.as_view(), name="resource-list"),
    path(
        "github/users/<str:username>/repositories/",
        GitHubPublicRepositoryListView.as_view(),
        name="github-public-repositories",
    ),
    path("leaderboard/", LeaderboardView.as_view(), name="leaderboard"),

    # Adaptive placement assessments
    path("tracks/<int:pk>/placement-quiz/", PlacementQuizView.as_view(), name="placement-quiz"),
    path("tracks/<int:pk>/placement-submit/", PlacementSubmitView.as_view(), name="placement-submit"),

    # Learning Path & Certificate endpoints
    path("paths/", LearningPathListCreateView.as_view(), name="path-list-create"),
    path("paths/<int:pk>/", LearningPathDetailView.as_view(), name="path-detail"),
    path("paths/<int:pk>/certificate/", CertificateDownloadView.as_view(), name="path-certificate"),

    # Item actions
    path("items/<int:pk>/complete/", MarkItemCompleteView.as_view(), name="item-complete"),
    path("items/<int:pk>/rate/", RateItemView.as_view(), name="item-rate"),
    path("items/<int:pk>/submission/", ProjectSubmissionView.as_view(), name="project-submission"),

    # Hosted coding challenges
    path("challenges/", CodingChallengeListView.as_view(), name="coding-challenge-list"),
    path("challenges/<slug:slug>/", CodingChallengeDetailView.as_view(), name="coding-challenge-detail"),
    path("challenges/<int:pk>/start/", CodingChallengeStartView.as_view(), name="coding-challenge-start"),
    path("challenge-attempts/<int:pk>/submit/", CodingChallengeSubmitView.as_view(), name="coding-challenge-submit"),
    path("arena/problems/", ArenaProblemListView.as_view(), name="arena-problem-list"),
    path("arena/problems/<int:pk>/submit/", ArenaProblemSubmitView.as_view(), name="arena-problem-submit"),
    path("arena/problems/<int:pk>/solution/", ArenaProblemSolutionView.as_view(), name="arena-problem-solution"),
    path("arena/submissions/", ArenaSubmissionHistoryView.as_view(), name="arena-submission-history"),
    path("arena/daily/", ArenaDailyChallengeView.as_view(), name="arena-daily-challenge"),

    # Dashboard analytics
    path("dashboard/stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
    path("analytics/skill-radar/", SkillRadarView.as_view(), name="skill-radar"),
]
