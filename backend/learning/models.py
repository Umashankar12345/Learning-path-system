from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, default="General")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Resource(models.Model):
    TYPE_CHOICES = [
        ("video", "Video"),
        ("article", "Article"),
        ("course", "Course"),
        ("project", "Project"),
    ]

    title = models.CharField(max_length=200)
    url = models.URLField(max_length=500)
    resource_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="course")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="resources")
    difficulty = models.IntegerField(default=1)  # 1 = Beginner, 2 = Intermediate, 3 = Advanced
    duration_minutes = models.IntegerField(default=30)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["difficulty", "order_hint", "id"] if hasattr(models.Model, "order_hint") else ["difficulty", "id"]

    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"


class LearningPath(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="learning_paths")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="learning_paths")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "skill")

    def __str__(self):
        return f"{self.user.username}'s path for {self.skill.name}"

    @property
    def total_items(self):
        return self.items.count()

    @property
    def completed_items(self):
        return self.items.filter(completed=True).count()

    @property
    def progress_percentage(self):
        total = self.total_items
        if total == 0:
            return 0
        return round((self.completed_items / total) * 100, 1)

    @property
    def total_duration_minutes(self):
        return sum(item.resource.duration_minutes for item in self.items.all())

    @property
    def completed_duration_minutes(self):
        return sum(item.resource.duration_minutes for item in self.items.filter(completed=True))


class PathItem(models.Model):
    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name="items")
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="path_items")
    order = models.IntegerField(default=1)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)  # 1 to 5 stars

    class Meta:
        ordering = ["order", "id"]
        unique_together = ("path", "resource")

    def __str__(self):
        status = "Done" if self.completed else "Pending"
        return f"Item {self.order}: {self.resource.title} [{status}]"

    def mark_complete(self):
        self.completed = True
        self.completed_at = timezone.now()
        self.save(update_fields=["completed", "completed_at"])

    def mark_incomplete(self):
        self.completed = False
        self.completed_at = None
        self.save(update_fields=["completed", "completed_at"])
