from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Skill, Resource, LearningPath, PathItem


class PathItemInline(admin.TabularInline):
    model = PathItem
    extra = 1
    fields = ("order", "resource", "completed", "completed_at", "rating")
    readonly_fields = ("completed_at",)


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
    Can view/add/change Skills and Resources, but cannot delete Users.
    """
    group, _ = Group.objects.get_or_create(name="Instructor")
    skill_ct = ContentType.objects.get_for_model(Skill)
    resource_ct = ContentType.objects.get_for_model(Resource)

    instructor_permissions = Permission.objects.filter(
        content_type__in=[skill_ct, resource_ct],
        codename__in=[
            "add_skill", "change_skill", "view_skill",
            "add_resource", "change_resource", "view_resource",
        ]
    )
    group.permissions.set(instructor_permissions)
    return group
