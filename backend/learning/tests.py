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

        # Check ordering: item 1 (diff 1), item 2 (diff 2), item 3 (diff 3)
        items = list(path.items.all().order_by("order"))
        self.assertEqual(items[0].resource.difficulty, 1)
        self.assertEqual(items[1].resource.difficulty, 2)
        self.assertEqual(items[2].resource.difficulty, 3)

    def test_mark_item_complete_and_rate(self):
        """Test marking an item complete records completed_at, and rating updates item."""
        self.client.force_authenticate(user=self.user1)

        # Create path
        path = LearningPath.objects.create(user=self.user1, skill=self.skill)
        item1 = PathItem.objects.create(path=path, resource=self.resource1, order=1)

        self.assertFalse(item1.completed)
        self.assertIsNone(item1.completed_at)

        # Mark complete
        url_complete = reverse("item-complete", kwargs={"pk": item1.id})
        response = self.client.post(url_complete, {"action": "complete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        item1.refresh_from_db()
        self.assertTrue(item1.completed)
        self.assertIsNotNone(item1.completed_at)

        # Rate item
        url_rate = reverse("item-rate", kwargs={"pk": item1.id})
        response = self.client.post(url_rate, {"rating": 5}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        item1.refresh_from_db()
        self.assertEqual(item1.rating, 5)

    def test_dashboard_metrics_from_real_database(self):
        """Test dashboard returns calculated values from actual database records."""
        self.client.force_authenticate(user=self.user1)

        # Create path with 2 items
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
        # resource1 has 60 minutes = 1.0 hour
        self.assertEqual(data["total_hours_learned"], 1.0)
        self.assertEqual(data["day_streak"], 1)
        # Next recommended should be item2
        self.assertIsNotNone(data["next_recommended_item"])
        self.assertEqual(data["next_recommended_item"]["id"], item2.id)

    def test_user_data_isolation(self):
        """Ensure user2 cannot mark complete or view user1's learning path items."""
        path1 = LearningPath.objects.create(user=self.user1, skill=self.skill)
        item1 = PathItem.objects.create(path=path1, resource=self.resource1, order=1)

        # Authenticate as user2
        self.client.force_authenticate(user=self.user2)

        # User2 tries to access user1's path detail
        url_path = reverse("path-detail", kwargs={"pk": path1.id})
        response = self.client.get(url_path)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # User2 tries to complete user1's item
        url_complete = reverse("item-complete", kwargs={"pk": item1.id})
        response = self.client.post(url_complete, {"action": "complete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
