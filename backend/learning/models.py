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


class PlacementQuestion(models.Model):
    class Difficulty(models.IntegerChoices):
        BEGINNER = 1, "Beginner"
        INTERMEDIATE = 2, "Intermediate"
        ADVANCED = 3, "Advanced"

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="placement_questions",
    )
    question_text = models.TextField()
    options = models.JSONField()
    correct_option = models.PositiveSmallIntegerField()
    difficulty = models.PositiveSmallIntegerField(choices=Difficulty.choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["difficulty", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["skill", "question_text"],
                name="unique_placement_question_per_skill",
            )
        ]

    def __str__(self):
        return f"{self.skill.name}: {self.question_text[:80]}"


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
    coding_challenge = models.ForeignKey(
        "CodingChallenge",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="associated_resources",
    )
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


class AssessmentAttempt(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assessment_attempts",
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="assessment_attempts",
    )
    score = models.PositiveSmallIntegerField()
    correct_answers = models.PositiveSmallIntegerField()
    total_questions = models.PositiveSmallIntegerField()
    recommended_level = models.PositiveSmallIntegerField(
        choices=PlacementQuestion.Difficulty.choices
    )
    skill_gap_breakdown = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.skill.name} placement ({self.score}%)"


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


class ProjectSubmission(models.Model):
    class ReviewStatus(models.TextChoices):
        PENDING = "pending", "Awaiting review"
        APPROVED = "approved", "Approved"
        REVISION = "revision", "Revision requested"

    item = models.OneToOneField(
        PathItem,
        on_delete=models.CASCADE,
        related_name="submission",
    )
    github_url = models.URLField(max_length=500)
    reflection = models.TextField(blank=True, max_length=2000)
    status = models.CharField(
        max_length=10,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
    )
    teacher_feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_project_submissions",
    )

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"Submission for {self.item.resource.title} by {self.item.path.user.username}"


class CodingChallenge(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=160)
    description = models.TextField()
    difficulty = models.CharField(
        max_length=8,
        choices=Difficulty.choices,
        default=Difficulty.EASY,
    )
    topic_tags = models.JSONField(default=list, blank=True)
    starter_code = models.TextField(blank=True)
    reference_solution = models.TextField(blank=True)
    language_id = models.PositiveSmallIntegerField(default=71)
    duration_minutes = models.PositiveSmallIntegerField(default=20)
    order = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    is_daily_challenge = models.BooleanField(default=False)
    challenge_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class CodingTestCase(models.Model):
    challenge = models.ForeignKey(
        CodingChallenge,
        on_delete=models.CASCADE,
        related_name="test_cases",
    )
    stdin = models.TextField(blank=True)
    expected_output = models.TextField()
    is_sample = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.challenge.title} test {self.order}"


class CodingAttempt(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "In progress"
        ACCEPTED = "accepted", "Accepted"
        PARTIAL = "partial", "Partially correct"
        WRONG_ANSWER = "wrong_answer", "Wrong answer"
        TIME_LIMIT = "time_limit", "Time limit exceeded"
        COMPILE_ERROR = "compile_error", "Compilation error"
        RUNTIME_ERROR = "runtime_error", "Runtime error"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="coding_attempts",
    )
    challenge = models.ForeignKey(
        CodingChallenge,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
    )
    source_code = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    passed_test_cases = models.PositiveSmallIntegerField(default=0)
    total_test_cases = models.PositiveSmallIntegerField(default=0)
    execution_time_ms = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user.username}: {self.challenge.title} ({self.status})"


class CodeSubmission(models.Model):
    class Status(models.TextChoices):
        ACCEPTED = "accepted", "Accepted"
        PARTIAL = "partial", "Partially correct"
        WRONG_ANSWER = "wrong_answer", "Wrong answer"
        TIME_LIMIT = "time_limit", "Time limit exceeded"
        COMPILE_ERROR = "compile_error", "Compilation error"
        RUNTIME_ERROR = "runtime_error", "Runtime error"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="code_submissions",
    )
    challenge = models.ForeignKey(
        CodingChallenge,
        on_delete=models.CASCADE,
        related_name="code_submissions",
    )
    language = models.CharField(max_length=32, default="python3")
    source_code = models.TextField()
    passed_count = models.PositiveSmallIntegerField(default=0)
    total_count = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=16, choices=Status.choices)
    runtime_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.challenge.title} ({self.status})"
