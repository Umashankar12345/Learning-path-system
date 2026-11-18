from datetime import timedelta
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from drf_spectacular.utils import extend_schema_field
from .models import (
    AssessmentAttempt,
    CodingAttempt,
    CodingChallenge,
    CodingTestCase,
    CodeSubmission,
    PlacementQuestion,
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


class TokenPairSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()


class SignupResponseSerializer(serializers.Serializer):
    user = UserSerializer()
    token = TokenPairSerializer()
    message = serializers.CharField()


class GoogleAuthRequestSerializer(serializers.Serializer):
    credential = serializers.CharField(required=False)
    id_token = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    name = serializers.CharField(required=False)


class GoogleAuthResponseSerializer(serializers.Serializer):
    user = UserSerializer()
    token = TokenPairSerializer()
    created = serializers.BooleanField()


class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()


class PathCompletionRequestSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=("toggle", "complete", "uncomplete"),
        required=False,
        default="toggle",
    )


class ItemRatingRequestSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)


class LearningPathCreateRequestSerializer(serializers.Serializer):
    skill_id = serializers.IntegerField(min_value=1)


class LeaderboardEntrySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    name = serializers.CharField()
    completed_count = serializers.IntegerField()
    hours_learned = serializers.FloatField()
    badges = serializers.ListField(child=serializers.DictField())
    rank = serializers.IntegerField()


class GitHubPublicRepositorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    full_name = serializers.CharField()
    html_url = serializers.URLField()
    description = serializers.CharField(allow_null=True, allow_blank=True)
    language = serializers.CharField(allow_null=True, allow_blank=True)
    stargazers_count = serializers.IntegerField()
    updated_at = serializers.DateTimeField()
    default_branch = serializers.CharField()


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
    coding_challenge_id = serializers.IntegerField(
        source="coding_challenge.id",
        read_only=True,
        allow_null=True,
    )
    coding_challenge_title = serializers.CharField(
        source="coding_challenge.title",
        read_only=True,
        allow_null=True,
    )

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
            "coding_challenge_id",
            "coding_challenge_title",
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
            "topic_tags",
            "starter_code",
            "duration_minutes",
            "is_daily_challenge",
            "challenge_date",
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


class CodeExecutionRequestSerializer(serializers.Serializer):
    source_code = serializers.CharField(max_length=20000, trim_whitespace=False)
    language = serializers.ChoiceField(choices=(("python3", "Python 3"),), default="python3")


class CodeSubmissionSerializer(serializers.ModelSerializer):
    challenge_title = serializers.CharField(source="challenge.title", read_only=True)

    class Meta:
        model = CodeSubmission
        fields = (
            "id",
            "challenge",
            "challenge_title",
            "language",
            "passed_count",
            "total_count",
            "status",
            "runtime_ms",
            "created_at",
        )
        read_only_fields = fields


class ArenaSubmissionResultSerializer(CodeSubmissionSerializer):
    test_results = serializers.ListField(child=serializers.DictField())

    class Meta(CodeSubmissionSerializer.Meta):
        fields = CodeSubmissionSerializer.Meta.fields + ("test_results",)


class PlacementQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacementQuestion
        fields = ("id", "question_text", "options", "difficulty")


class PlacementAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(min_value=1)
    selected_option = serializers.IntegerField(min_value=0, max_value=3)


class PlacementSubmissionSerializer(serializers.Serializer):
    answers = PlacementAnswerSerializer(many=True, allow_empty=False)


class PlacementSkillGapSerializer(serializers.Serializer):
    difficulty = serializers.IntegerField()
    label = serializers.CharField()
    correct = serializers.IntegerField()
    total = serializers.IntegerField()
    accuracy = serializers.IntegerField()
    status = serializers.ChoiceField(choices=("needs_work", "developing", "strong"))


class PlacementResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    score = serializers.IntegerField()
    correct_answers = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    recommended_level = serializers.IntegerField()
    recommended_level_label = serializers.CharField()
    path_id = serializers.IntegerField()
    skill_gap_breakdown = PlacementSkillGapSerializer(many=True)
    created_at = serializers.DateTimeField()


class ReferenceSolutionSerializer(serializers.Serializer):
    challenge_id = serializers.IntegerField()
    challenge_title = serializers.CharField()
    language = serializers.CharField()
    reference_solution = serializers.CharField()


class ArenaDailyChallengeSerializer(serializers.Serializer):
    challenge = CodingChallengeSerializer()
    coding_streak = serializers.IntegerField()
    completed_today = serializers.BooleanField()


class SkillRadarPointSerializer(serializers.Serializer):
    topic = serializers.CharField()
    completed_modules = serializers.IntegerField()
    total_modules = serializers.IntegerField()
    study_hours = serializers.FloatField()
    quiz_score = serializers.IntegerField()
    score = serializers.IntegerField()


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


class WeeklyActivitySerializer(serializers.Serializer):
    date = serializers.DateField()
    day = serializers.CharField()
    hours = serializers.FloatField()
    minutes = serializers.IntegerField()


class DashboardStatsSerializer(serializers.Serializer):
    active_paths_count = serializers.IntegerField()
    total_items = serializers.IntegerField()
    completed_items = serializers.IntegerField()
    overall_progress = serializers.FloatField()
    total_hours_learned = serializers.FloatField()
    day_streak = serializers.IntegerField()
    next_recommended_item = PathItemSerializer(allow_null=True)
    weekly_activity = WeeklyActivitySerializer(many=True)
    paths = LearningPathSerializer(many=True)
