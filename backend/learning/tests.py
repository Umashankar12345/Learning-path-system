from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from django.utils import timezone

from .models import Skill, Resource, LearningPath, PathItem


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

    def test_google_oauth_endpoint(self):
        """Test Google login endpoint registers or signs in user."""
        url = reverse("google-auth")
        data = {
            "email": "google_learner@example.com",
            "name": "Google User",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertTrue(User.objects.filter(email="google_learner@example.com").exists())

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
