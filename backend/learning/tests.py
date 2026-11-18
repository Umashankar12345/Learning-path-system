from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from django.utils import timezone
from django.test import override_settings
from unittest.mock import patch

from .models import (
    CodingAttempt,
    CodingChallenge,
    Skill,
    Resource,
    LearningPath,
    PathItem,
    ProjectSubmission,
)
from .judge import run_test_case


class LearningPathAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test users
        self.user1 = User.objects.create_user(
            username="user_one", email="user1@example.com", password="SecurePassword123!"
        )
        self.user2 = User.objects.create_user(
            username="user_two", email="user2@example.com", password="SecurePassword123!"
        )

        # Create test skills
        self.skill = Skill.objects.create(
            name="Python for Data Science",
            description="Learn Python data analysis",
            category="Data Science",
        )

        # Create resources with different difficulties & durations
        self.resource1 = Resource.objects.create(
            title="Python Basics",
            url="https://example.com/basics",
            resource_type="video",
            skill=self.skill,
            difficulty=1,
            duration_minutes=60,
        )
        self.resource2 = Resource.objects.create(
            title="Pandas and NumPy",
            url="https://example.com/pandas",
            resource_type="article",
            skill=self.skill,
            difficulty=2,
            duration_minutes=60,
        )
        self.resource3 = Resource.objects.create(
            title="Machine Learning Models",
            url="https://example.com/ml",
            resource_type="course",
            skill=self.skill,
            difficulty=3,
            duration_minutes=120,
        )

    def test_user_signup(self):
        """Test signup creates a new user and returns JWT tokens."""
        url = reverse("signup")
        data = {
            "username": "new_learner",
            "email": "learner@test.com",
            "password": "LearnerPassword999!",
            "password_confirm": "LearnerPassword999!",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertIn("access", response.data["token"])
        self.assertTrue(User.objects.filter(username="new_learner").exists())

    @patch.dict("os.environ", {"GOOGLE_CLIENT_ID": "test-google-client-id"})
    @patch("google.oauth2.id_token.verify_oauth2_token")
    def test_google_oauth_endpoint(self, verify_token):
        """Test Google login endpoint verifies credentials and registers a user."""
        verify_token.return_value = {
            "email": "google_learner@example.com",
            "name": "Google User",
            "email_verified": True,
        }
        url = reverse("google-auth")
        response = self.client.post(url, {"credential": "verified-google-jwt"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIn("token", response.data)
        self.assertTrue(User.objects.filter(email="google_learner@example.com").exists())

    @patch.dict("os.environ", {"GOOGLE_CLIENT_ID": "test-google-client-id"})
    @patch("google.oauth2.id_token.verify_oauth2_token")
    def test_google_oauth_rejects_unverified_payload(self, verify_token):
        verify_token.return_value = {
            "email": "fake@example.com",
            "name": "Fake Google User",
            "email_verified": False,
        }
        url = reverse("google-auth")
        response = self.client.post(
            url,
            {"credential": "unverified-google-jwt"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email="fake@example.com").exists())

    @patch.dict("os.environ", {"GOOGLE_CLIENT_ID": ""})
    def test_google_oauth_requires_client_id(self):
        response = self.client.post(
            reverse("google-auth"),
            {"credential": "google-jwt"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("GOOGLE_CLIENT_ID", response.data["error"])

    def test_create_learning_path_ordered_by_difficulty(self):
        """Test creating a learning path populates items ordered by difficulty."""
        self.client.force_authenticate(user=self.user1)
        url = reverse("path-list-create")
        response = self.client.post(url, {"skill_id": self.skill.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        path_id = response.data["id"]
        path = LearningPath.objects.get(id=path_id)
        self.assertEqual(path.user, self.user1)
        self.assertEqual(path.items.count(), 3)

        items = list(path.items.all().order_by("order"))
        self.assertEqual(items[0].resource.difficulty, 1)
        self.assertEqual(items[1].resource.difficulty, 2)
        self.assertEqual(items[2].resource.difficulty, 3)

    def test_mark_item_complete_and_rate(self):
        """Test marking an item complete records completed_at, and rating updates item."""
        self.client.force_authenticate(user=self.user1)

        path = LearningPath.objects.create(user=self.user1, skill=self.skill)
        item1 = PathItem.objects.create(path=path, resource=self.resource1, order=1)

        self.assertFalse(item1.completed)
        self.assertIsNone(item1.completed_at)

        url_complete = reverse("item-complete", kwargs={"pk": item1.id})
        response = self.client.post(url_complete, {"action": "complete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        item1.refresh_from_db()
        self.assertTrue(item1.completed)
        self.assertIsNotNone(item1.completed_at)

        url_rate = reverse("item-rate", kwargs={"pk": item1.id})
        response = self.client.post(url_rate, {"rating": 5}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        item1.refresh_from_db()
        self.assertEqual(item1.rating, 5)

    def test_project_submission_is_teacher_reviewable_and_owner_scoped(self):
        project = Resource.objects.create(
            title="Build a learning tracker",
            url="https://example.com/tracker",
            resource_type="project",
            skill=self.skill,
            difficulty=2,
        )
        path = LearningPath.objects.create(user=self.user1, skill=self.skill)
        item = PathItem.objects.create(path=path, resource=project, order=1)
        url = reverse("project-submission", kwargs={"pk": item.id})
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            url,
            {
                "github_url": "https://github.com/learner/learning-tracker",
                "reflection": "Built the data model and progress view.",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], ProjectSubmission.ReviewStatus.PENDING)

        submission = ProjectSubmission.objects.get(item=item)
        submission.status = ProjectSubmission.ReviewStatus.APPROVED
        submission.teacher_feedback = "Good data model and clear README."
        submission.reviewed_by = self.user2
        submission.save()

        detail = self.client.get(reverse("path-detail", kwargs={"pk": path.id}))
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(
            detail.data["items"][0]["submission"]["teacher_feedback"],
            "Good data model and clear README.",
        )

        response = self.client.post(
            url,
            {
                "github_url": "https://github.com/learner/learning-tracker-v2",
                "reflection": "Addressed teacher feedback.",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        submission.refresh_from_db()
        self.assertEqual(submission.status, ProjectSubmission.ReviewStatus.PENDING)
        self.assertEqual(submission.teacher_feedback, "")
        self.assertIsNone(submission.reviewed_by)

        self.client.force_authenticate(user=self.user2)
        response = self.client.post(
            url,
            {"github_url": "https://github.com/learner/other-project"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_project_submission_rejects_non_github_urls_and_non_project_items(self):
        path = LearningPath.objects.create(user=self.user1, skill=self.skill)
        item = PathItem.objects.create(path=path, resource=self.resource1, order=1)
        self.client.force_authenticate(user=self.user1)
        url = reverse("project-submission", kwargs={"pk": item.id})

        response = self.client.post(
            url,
            {"github_url": "https://github.com/learner/my-project"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

        project = Resource.objects.create(
            title="Build a portfolio",
            url="https://example.com/portfolio",
            resource_type="project",
            skill=self.skill,
            difficulty=2,
        )
        project_item = PathItem.objects.create(path=path, resource=project, order=2)
        response = self.client.post(
            reverse("project-submission", kwargs={"pk": project_item.id}),
            {"github_url": "https://github.com/not-a-repository"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("github_url", response.data)

    def test_coding_challenge_catalog_has_real_sample_and_hidden_cases(self):
        response = self.client.get(reverse("coding-challenge-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        challenge = next(
            item for item in response.data if item["slug"] == "sum-two-integers"
        )
        self.assertEqual(challenge["test_case_count"], 3)
        self.assertEqual(len(challenge["sample_test_cases"]), 2)

    @override_settings(JUDGE0_API_URL="https://judge0.example")
    def test_coding_challenge_starts_timed_attempt_and_judges_all_cases(self):
        self.client.force_authenticate(user=self.user1)
        challenge = CodingChallenge.objects.get(slug="sum-two-integers")
        start = self.client.post(
            reverse("coding-challenge-start", kwargs={"pk": challenge.id}),
            format="json",
        )
        self.assertEqual(start.status_code, status.HTTP_201_CREATED)
        self.assertEqual(start.data["status"], CodingAttempt.Status.IN_PROGRESS)
        self.assertIn("solve()", start.data["starter_code"])
        attempt_id = start.data["id"]

        with patch(
            "learning.views.run_test_case",
            side_effect=[
                {"status": "accepted", "time": "0.01"},
                {"status": "accepted", "time": "0.02"},
                {"status": "wrong_answer", "time": "0.03"},
            ],
        ) as judge:
            response = self.client.post(
                reverse("coding-challenge-submit", kwargs={"pk": attempt_id}),
                {"source_code": "print(sum(map(int, input().split())))"},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], CodingAttempt.Status.PARTIAL)
        self.assertEqual(response.data["passed_test_cases"], 2)
        self.assertEqual(response.data["total_test_cases"], 3)
        self.assertEqual(len(response.data["test_results"]), 3)
        self.assertNotIn("expected_output", response.data["test_results"][2])
        self.assertEqual(judge.call_count, 3)

        attempt = CodingAttempt.objects.get(pk=attempt_id)
        self.assertEqual(attempt.source_code, "print(sum(map(int, input().split())))")
        self.assertIsNotNone(attempt.submitted_at)

    @override_settings(JUDGE0_API_URL="")
    def test_coding_challenge_refuses_to_start_without_live_judge_config(self):
        self.client.force_authenticate(user=self.user1)
        challenge = CodingChallenge.objects.get(slug="sum-two-integers")
        response = self.client.post(
            reverse("coding-challenge-start", kwargs={"pk": challenge.id}),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(CodingAttempt.objects.count(), 0)

    @override_settings(JUDGE0_API_URL="https://judge0.example")
    def test_coding_challenge_attempt_is_owner_scoped_and_timer_enforced(self):
        challenge = CodingChallenge.objects.get(slug="sum-two-integers")
        attempt = CodingAttempt.objects.create(user=self.user1, challenge=challenge)
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(
            reverse("coding-challenge-submit", kwargs={"pk": attempt.id}),
            {"source_code": "print(1)"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(user=self.user1)
        attempt.started_at = timezone.now() - timedelta(minutes=challenge.duration_minutes + 1)
        attempt.save(update_fields=["started_at"])
        with patch("learning.views.run_test_case") as judge:
            response = self.client.post(
                reverse("coding-challenge-submit", kwargs={"pk": attempt.id}),
                {"source_code": "print(1)"},
                format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        judge.assert_not_called()

    @override_settings(
        JUDGE0_API_URL="https://judge0.example/api",
        JUDGE0_API_KEY="test-api-key",
        JUDGE0_API_HOST="judge0.example",
    )
    @patch("learning.judge.time.sleep")
    @patch("learning.judge.requests.get")
    @patch("learning.judge.requests.post")
    def test_judge0_client_sends_limits_and_reads_real_submission_result(
        self, post, get, _sleep
    ):
        post.return_value.json.return_value = {"token": "submission-token"}
        get.return_value.json.return_value = {
            "status": {"id": 3, "description": "Accepted"},
            "stdout": "5\n",
            "time": "0.01",
            "memory": 1024,
        }

        result = run_test_case(
            source_code="print(sum(map(int, input().split())))",
            language_id=71,
            stdin="2 3\n",
            expected_output="5\n",
        )

        self.assertEqual(result["status"], "accepted")
        self.assertEqual(result["stdout"], "5\n")
        payload = post.call_args.kwargs["json"]
        self.assertEqual(payload["cpu_time_limit"], 2)
        self.assertEqual(payload["wall_time_limit"], 5)
        self.assertEqual(payload["memory_limit"], 128000)
        self.assertEqual(post.call_args.kwargs["headers"]["X-RapidAPI-Key"], "test-api-key")
        self.assertIn("/submissions/submission-token", get.call_args.args[0])

    def test_pdf_certificate_download(self):
        """Test generating and downloading PDF Certificate of Completion."""
        self.client.force_authenticate(user=self.user1)
        path = LearningPath.objects.create(user=self.user1, skill=self.skill)
        PathItem.objects.create(path=path, resource=self.resource1, order=1, completed=True)

        url_cert = reverse("path-certificate", kwargs={"pk": path.id})
        response = self.client.get(url_cert)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(len(response.content) > 1000)

    def test_leaderboard_hides_staff_and_zero_progress_and_ranks_correctly(self):
        """
        Verify:
        1. Staff/admin users are hidden from the leaderboard.
        2. Users with 0 completions are hidden (board starts empty and fills with real activity).
        3. Learner B (more completed hours) is ranked #1, Learner A is ranked #2.
        """
        # User 1 completes 1 item (60 mins = 1.0 hr)
        path1 = LearningPath.objects.create(user=self.user1, skill=self.skill)
        PathItem.objects.create(path=path1, resource=self.resource1, order=1, completed=True)

        # User 2 completes 2 items (60 mins + 60 mins = 120 mins = 2.0 hrs)
        path2 = LearningPath.objects.create(user=self.user2, skill=self.skill)
        PathItem.objects.create(path=path2, resource=self.resource1, order=1, completed=True)
        PathItem.objects.create(path=path2, resource=self.resource2, order=2, completed=True)

        # Create user 3 with 0 completions
        user3 = User.objects.create_user(username="zero_progress", password="Password123!")
        LearningPath.objects.create(user=user3, skill=self.skill)

        # Create staff user with completions
        staff_user = User.objects.create_user(username="admin_staff", is_staff=True, password="Password123!")
        staff_path = LearningPath.objects.create(user=staff_user, skill=self.skill)
        PathItem.objects.create(path=staff_path, resource=self.resource3, order=1, completed=True)

        url = reverse("leaderboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        usernames = [entry["username"] for entry in data]

        # Verify staff and zero-progress users are excluded
        self.assertNotIn("admin_staff", usernames)
        self.assertNotIn("zero_progress", usernames)

        # Verify exactly user2 and user1 are present
        self.assertEqual(len(data), 2)

        # Verify ranking order: User 2 is Rank #1 (2.0 hrs), User 1 is Rank #2 (1.0 hr)
        self.assertEqual(data[0]["username"], self.user2.username)
        self.assertEqual(data[0]["rank"], 1)
        self.assertEqual(data[0]["hours_learned"], 2.0)
        self.assertEqual(data[0]["completed_count"], 2)

        self.assertEqual(data[1]["username"], self.user1.username)
        self.assertEqual(data[1]["rank"], 2)
        self.assertEqual(data[1]["hours_learned"], 1.0)
        self.assertEqual(data[1]["completed_count"], 1)

    def test_swagger_schema_endpoint(self):
        """Test OpenAPI schema generation."""
        url = reverse("schema")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dashboard_metrics_from_real_database(self):
        """Test dashboard returns calculated values from actual database records."""
        self.client.force_authenticate(user=self.user1)

        path = LearningPath.objects.create(user=self.user1, skill=self.skill)
        item1 = PathItem.objects.create(
            path=path,
            resource=self.resource1,
            order=1,
            completed=True,
            completed_at=timezone.now(),
        )
        item2 = PathItem.objects.create(
            path=path,
            resource=self.resource2,
            order=2,
            completed=False,
        )

        url = reverse("dashboard-stats")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data["active_paths_count"], 1)
        self.assertEqual(data["total_items"], 2)
        self.assertEqual(data["completed_items"], 1)
        self.assertEqual(data["overall_progress"], 50.0)
        self.assertEqual(data["total_hours_learned"], 1.0)
        self.assertEqual(data["day_streak"], 1)
        self.assertIsNotNone(data["next_recommended_item"])
        self.assertEqual(data["next_recommended_item"]["id"], item2.id)

    def test_user_data_isolation(self):
        """Ensure user2 cannot mark complete or view user1's learning path items."""
        path1 = LearningPath.objects.create(user=self.user1, skill=self.skill)
        item1 = PathItem.objects.create(path=path1, resource=self.resource1, order=1)

        self.client.force_authenticate(user=self.user2)

        url_path = reverse("path-detail", kwargs={"pk": path1.id})
        response = self.client.get(url_path)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url_complete = reverse("item-complete", kwargs={"pk": item1.id})
        response = self.client.post(url_complete, {"action": "complete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
