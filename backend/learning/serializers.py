from datetime import timedelta
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from drf_spectacular.utils import extend_schema_field
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


class ProjectSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectSubmission
        fields = (
            "github_url",
            "reflection",
            "status",
            "teacher_feedback",
            "submitted_at",
            "reviewed_at",
        )
        read_only_fields = ("status", "teacher_feedback", "submitted_at", "reviewed_at")

    def validate_github_url(self, value):
        from urllib.parse import urlparse

        parsed_url = urlparse(value)
        path_parts = [part for part in parsed_url.path.split("/") if part]
        if (
            parsed_url.scheme != "https"
            or parsed_url.hostname != "github.com"
            or len(path_parts) < 2
        ):
            raise serializers.ValidationError(
                "Enter a public GitHub repository URL, such as https://github.com/owner/repository."
            )
        return value


class CodingTestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodingTestCase
        fields = ("stdin", "expected_output", "order")


class CodingChallengeSerializer(serializers.ModelSerializer):
    sample_test_cases = serializers.SerializerMethodField()
    test_case_count = serializers.SerializerMethodField()

    class Meta:
        model = CodingChallenge
        fields = (
            "id",
            "slug",
            "title",
            "description",
            "difficulty",
            "starter_code",
            "duration_minutes",
            "sample_test_cases",
            "test_case_count",
        )

    @extend_schema_field(CodingTestCaseSerializer(many=True))
    def get_sample_test_cases(self, obj):
        examples = obj.test_cases.filter(is_sample=True)
        return CodingTestCaseSerializer(examples, many=True).data

    @extend_schema_field(serializers.IntegerField)
    def get_test_case_count(self, obj):
        return obj.test_cases.count()


class CodingAttemptSerializer(serializers.ModelSerializer):
    expires_at = serializers.SerializerMethodField()

    class Meta:
        model = CodingAttempt
        fields = (
            "id",
            "challenge",
            "status",
            "started_at",
            "submitted_at",
            "expires_at",
            "passed_test_cases",
            "total_test_cases",
            "execution_time_ms",
        )
        read_only_fields = fields

    @extend_schema_field(serializers.DateTimeField)
    def get_expires_at(self, instance):
        return instance.started_at + timedelta(minutes=instance.challenge.duration_minutes)


class CodingAttemptStartSerializer(CodingAttemptSerializer):
    starter_code = serializers.CharField(source="challenge.starter_code", read_only=True)
    language_id = serializers.IntegerField(source="challenge.language_id", read_only=True)

    class Meta(CodingAttemptSerializer.Meta):
        fields = CodingAttemptSerializer.Meta.fields + ("starter_code", "language_id")


class CodingTestResultSerializer(serializers.Serializer):
    order = serializers.IntegerField()
    is_sample = serializers.BooleanField()
    passed = serializers.BooleanField()
    status = serializers.CharField()
    diagnostic = serializers.CharField(required=False)


class CodingAttemptResultSerializer(CodingAttemptSerializer):
    test_results = CodingTestResultSerializer(many=True)

    class Meta(CodingAttemptSerializer.Meta):
        fields = CodingAttemptSerializer.Meta.fields + ("test_results",)


class CodeSubmissionSerializer(serializers.Serializer):
    source_code = serializers.CharField(max_length=20000, trim_whitespace=False)


class PathItemSerializer(serializers.ModelSerializer):
    resource = ResourceSerializer(read_only=True)
    submission = ProjectSubmissionSerializer(read_only=True)
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
            "submission",
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
