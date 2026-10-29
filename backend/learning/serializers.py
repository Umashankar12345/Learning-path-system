from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from drf_spectacular.utils import extend_schema_field
from .models import Skill, Resource, LearningPath, PathItem

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "date_joined")
        read_only_fields = ("id", "date_joined")


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password", "password_confirm")

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user


class ResourceSerializer(serializers.ModelSerializer):
    skill_name = serializers.ReadOnlyField(source="skill.name")

    class Meta:
        model = Resource
        fields = (
            "id",
            "title",
            "url",
            "resource_type",
            "skill",
            "skill_name",
            "difficulty",
            "duration_minutes",
            "description",
            "created_at",
        )


class SkillSerializer(serializers.ModelSerializer):
    resource_count = serializers.SerializerMethodField()

    class Meta:
        model = Skill
        fields = ("id", "name", "description", "category", "resource_count", "created_at")

    @extend_schema_field(serializers.IntegerField)
    def get_resource_count(self, obj):
        return obj.resources.count()


class PathItemSerializer(serializers.ModelSerializer):
    resource = ResourceSerializer(read_only=True)
    resource_id = serializers.PrimaryKeyRelatedField(
        queryset=Resource.objects.all(), source="resource", write_only=True
    )

    class Meta:
        model = PathItem
        fields = (
            "id",
            "path",
            "resource",
            "resource_id",
            "order",
            "completed",
            "completed_at",
            "rating",
        )
        read_only_fields = ("id", "path", "completed_at")


class LearningPathSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), source="skill", write_only=True
    )
    total_items = serializers.IntegerField(read_only=True)
    completed_items = serializers.IntegerField(read_only=True)
    progress_percentage = serializers.FloatField(read_only=True)
    total_duration_minutes = serializers.IntegerField(read_only=True)
    completed_duration_minutes = serializers.IntegerField(read_only=True)

    class Meta:
        model = LearningPath
        fields = (
            "id",
            "user",
            "skill",
            "skill_id",
            "created_at",
            "updated_at",
            "total_items",
            "completed_items",
            "progress_percentage",
            "total_duration_minutes",
            "completed_duration_minutes",
        )
        read_only_fields = ("id", "user", "created_at", "updated_at")


class LearningPathDetailSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)
    items = PathItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    completed_items = serializers.IntegerField(read_only=True)
    progress_percentage = serializers.FloatField(read_only=True)
    total_duration_minutes = serializers.IntegerField(read_only=True)
    completed_duration_minutes = serializers.IntegerField(read_only=True)

    class Meta:
        model = LearningPath
        fields = (
            "id",
            "user",
            "skill",
            "created_at",
            "updated_at",
            "total_items",
            "completed_items",
            "progress_percentage",
            "total_duration_minutes",
            "completed_duration_minutes",
            "items",
        )
        read_only_fields = ("id", "user", "created_at", "updated_at")
