from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import (
    CodingAttempt,
    CodingChallenge,
    CodingTestCase,
    Skill,
    Resource,
    LearningPath,
    PathItem,
    ProjectSubmission,
)


class PathItemInline(admin.TabularInline):
    model = PathItem
    extra = 1
    fields = ("order", "resource", "completed", "completed_at", "rating")
    readonly_fields = ("completed_at",)


@admin.register(ProjectSubmission)
class ProjectSubmissionAdmin(admin.ModelAdmin):
    list_display = ("item", "get_learner", "status", "submitted_at", "reviewed_by")
    list_filter = ("status", "submitted_at")
    search_fields = ("item__path__user__username", "item__resource__title", "github_url")
    readonly_fields = ("submitted_at",)
    fields = (
        "item",
        "github_url",
        "reflection",
        "status",
        "teacher_feedback",
        "submitted_at",
        "reviewed_at",
        "reviewed_by",
    )

    def get_learner(self, obj):
        return obj.item.path.user
    get_learner.short_description = "Learner"

    def save_model(self, request, obj, form, change):
        if obj.status != ProjectSubmission.ReviewStatus.PENDING:
            obj.reviewed_by = request.user
            if not obj.reviewed_at:
                from django.utils import timezone

                obj.reviewed_at = timezone.now()
        else:
            obj.reviewed_by = None
            obj.reviewed_at = None
        super().save_model(request, obj, form, change)


class CodingTestCaseInline(admin.TabularInline):
    model = CodingTestCase
    extra = 1


@admin.register(CodingChallenge)
class CodingChallengeAdmin(admin.ModelAdmin):
    list_display = ("title", "difficulty", "duration_minutes", "is_active", "order")
    list_filter = ("difficulty", "is_active")
    search_fields = ("title", "description", "slug")
    inlines = [CodingTestCaseInline]


@admin.register(CodingAttempt)
class CodingAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "challenge",
        "status",
        "passed_test_cases",
        "total_test_cases",
        "started_at",
        "submitted_at",
    )
    list_filter = ("status", "challenge", "started_at")
    search_fields = ("user__username", "challenge__title")
    readonly_fields = (
        "user",
        "challenge",
        "status",
        "source_code",
        "started_at",
        "submitted_at",
        "passed_test_cases",
        "total_test_cases",
        "execution_time_ms",
    )
    fields = readonly_fields


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "get_resource_count", "created_at")
    search_fields = ("name", "description", "category")
    list_filter = ("category", "created_at")

    def get_resource_count(self, obj):
        return obj.resources.count()
    get_resource_count.short_description = "Resources"


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "skill", "resource_type", "difficulty", "duration_minutes")
    search_fields = ("title", "url", "description")
    list_filter = ("resource_type", "difficulty", "skill")
    ordering = ("skill", "difficulty", "id")


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ("user", "skill", "get_progress", "created_at", "updated_at")
    search_fields = ("user__username", "user__email", "skill__name")
    list_filter = ("skill", "created_at")
    inlines = [PathItemInline]

    def get_progress(self, obj):
        return f"{obj.progress_percentage}% ({obj.completed_items}/{obj.total_items})"
    get_progress.short_description = "Progress"


@admin.register(PathItem)
class PathItemAdmin(admin.ModelAdmin):
    list_display = ("id", "path", "resource", "order", "completed", "completed_at", "rating")
    list_filter = ("completed", "rating", "path__skill")
    search_fields = ("resource__title", "path__user__username")


def setup_instructor_group():
    """
    Utility to create/configure Instructor group permissions:
    Can manage Skills and Resources and review project submissions.
    """
    group, _ = Group.objects.get_or_create(name="Instructor")
    skill_ct = ContentType.objects.get_for_model(Skill)
    resource_ct = ContentType.objects.get_for_model(Resource)
    submission_ct = ContentType.objects.get_for_model(ProjectSubmission)
    challenge_ct = ContentType.objects.get_for_model(CodingChallenge)
    test_case_ct = ContentType.objects.get_for_model(CodingTestCase)

    instructor_permissions = Permission.objects.filter(
        content_type__in=[
            skill_ct,
            resource_ct,
            submission_ct,
            challenge_ct,
            test_case_ct,
        ],
        codename__in=[
            "add_skill", "change_skill", "view_skill",
            "add_resource", "change_resource", "view_resource",
            "view_projectsubmission", "change_projectsubmission",
            "add_codingchallenge", "change_codingchallenge", "view_codingchallenge",
            "add_codingtestcase", "change_codingtestcase", "view_codingtestcase",
        ]
    )
    group.permissions.set(instructor_permissions)
    return group
