from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from gymApp.models import (
    Address,
    BugReport,
    ClientProfile,
    DifficultyLevel,
    Equipment,
    Exercise,
    ExerciseType,
    Gym,
    MobileTextContent,
    NewFeatureRequest,
    Subscription,
    SubscriptionPlan,
    WorkoutDay,
    WorkoutDayLog,
    WorkoutItem,
    WorkoutItemLog,
    WorkoutPlan,
    WorkoutPlanRun,
    WorkoutSetLog,
)


class DifficultyLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DifficultyLevel
        fields = ["id", "name"]


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ["id", "name"]


class ExerciseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseType
        fields = ["id", "name"]


class ExerciseSerializer(serializers.ModelSerializer):
    equipments = EquipmentSerializer(many=True, read_only=True)
    exercise_type = ExerciseTypeSerializer(read_only=True)
    difficulty_level = DifficultyLevelSerializer(read_only=True)

    class Meta:
        model = Exercise
        fields = [
            "id",
            "name",
            "description",
            "metabolic_equivalent",
            "video",
            "thumbnail",
            "amount_unit",
            "equipments",
            "exercise_type",
            "difficulty_level",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "equipments",
            "exercise_type",
            "difficulty_level",
        ]


class WorkoutPlanSerializer(serializers.ModelSerializer):
    workout_days = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    difficulty_level = DifficultyLevelSerializer(read_only=True)

    class Meta:
        model = WorkoutPlan
        fields = [
            "id",
            "name",
            "description",
            "difficulty_level",
            "workout_days",
            "created_at",
            "updated_at",
        ]


class WorkoutDaySerializer(serializers.ModelSerializer):
    workout_items = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = WorkoutDay
        fields = [
            "id",
            "day_number",
            "description",
            "workout_items",
            "created_at",
            "updated_at",
        ]


class WorkoutSetLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutSetLog
        fields = ["id", "set_number", "actual_amount", "weight"]


class WorkoutItemSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)

    class Meta:
        model = WorkoutItem
        fields = ["id", "amount", "sets", "order", "exercise"]


class WorkoutItemLogSerializer(serializers.ModelSerializer):
    set_logs = WorkoutSetLogSerializer(many=True, read_only=True)

    class Meta:
        model = WorkoutItemLog
        fields = ["id", "completed", "notes", "set_logs"]


class WorkoutDayLogSerializer(serializers.ModelSerializer):
    item_logs = WorkoutItemLogSerializer(many=True, read_only=True)
    description = serializers.CharField(source="workout_day.description", read_only=True)
    workout_day_order_number = serializers.IntegerField(
        source="workout_day.day_number", read_only=True
    )

    class Meta:
        model = WorkoutDayLog
        fields = [
            "id",
            "date",
            "completed",
            "item_logs",
            "description",
            "workout_day_order_number",
        ]


class WorkoutItemLogDetailSerializer(serializers.ModelSerializer):
    set_logs = WorkoutSetLogSerializer(many=True, read_only=True)
    workout_item = WorkoutItemSerializer(read_only=True)

    class Meta:
        model = WorkoutItemLog
        fields = ["id", "completed", "notes", "set_logs", "workout_item"]


class WorkoutDayDetailedLogSerializer(serializers.ModelSerializer):
    item_logs = WorkoutItemLogDetailSerializer(many=True, read_only=True)
    description = serializers.CharField(source="workout_day.description", read_only=True)
    day_number = serializers.IntegerField(source="workout_day.day_number", read_only=True)

    class Meta:
        model = WorkoutDayLog
        fields = [
            "id",
            "date",
            "completed",
            "item_logs",
            "description",
            "day_number",
        ]


class WorkoutItemDetailedLogSerializer(serializers.ModelSerializer):
    set_logs = WorkoutSetLogSerializer(many=True, read_only=True)
    workout_item = WorkoutItemSerializer(read_only=True)

    class Meta:
        model = WorkoutItemLog
        fields = ["id", "completed", "notes", "set_logs", "workout_item"]


class FlatWorkoutPlanSerializer(serializers.ModelSerializer):
    difficulty_level = DifficultyLevelSerializer(read_only=True)

    class Meta:
        model = WorkoutPlan
        fields = ["id", "name", "description", "difficulty_level"]


class WorkoutPlanRunSerializer(serializers.ModelSerializer):
    workout_plan = FlatWorkoutPlanSerializer(read_only=True)
    day_logs = WorkoutDayLogSerializer(many=True, read_only=True)

    class Meta:
        model = WorkoutPlanRun
        fields = [
            "id",
            "workout_plan",
            "started_at",
            "finished_at",
            "is_active",
            "day_logs",
        ]


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    workout_plans = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = SubscriptionPlan
        fields = [
            "id",
            "name",
            "price",
            "stripe_price_id",
            "features",
            "workout_plans",
            "created_at",
            "updated_at",
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = [
            "id",
            "status",
            "current_period_start",
            "current_period_end",
            "cancel_at_period_end",
            "canceled_at",
            "ended_at",
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "email", "first_name", "last_name"]


class ClientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    subscription_start = serializers.SerializerMethodField()
    subscription_end = serializers.SerializerMethodField()

    class Meta:
        model = ClientProfile
        fields = [
            "user",
            "subscription_plan",
            "subscription_start",
            "subscription_end",
            "active_workout_plan",
            "age",
            "weight",
            "height",
            "goals",
            "verified",
        ]

        extra_kwargs = {
            "subscription_plan": {"required": False, "allow_null": True},
            "active_workout_plan": {"required": False, "allow_null": True},
            "age": {"required": False, "allow_null": True},
            "weight": {"required": False, "allow_null": True},
            "height": {"required": False, "allow_null": True},
            "goals": {"required": False, "allow_null": True, "allow_blank": True},
        }

    def _get_latest_subscription(self, obj: ClientProfile) -> Subscription | None:
        return Subscription.objects.filter(user=obj.user).order_by("-created_at").first()

    def get_subscription_start(self, obj: ClientProfile):
        sub = self._get_latest_subscription(obj)
        return getattr(sub, "current_period_start", None) if sub else None

    def get_subscription_end(self, obj: ClientProfile):
        sub = self._get_latest_subscription(obj)
        return getattr(sub, "current_period_end", None) if sub else None


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, value: str):
        User = get_user_model()
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value: str):
        User = get_user_model()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        User = get_user_model()

        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()

        ClientProfile.objects.get_or_create(user=user)

        return user


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PaymentIntentCreateSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1)


class SubscriptionCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    price_id = serializers.CharField()


class BugReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = BugReport
        fields = ["id", "title", "description", "screenshot", "created_at"]
        read_only_fields = ["id", "created_at"]


class NewFeatureRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewFeatureRequest
        fields = ["id", "title", "description", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "street",
            "city",
            "state",
            "postal_code",
            "country",
            "latitude",
            "longitude",
        ]


class GymSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    equipments = EquipmentSerializer(many=True, read_only=True)

    class Meta:
        model = Gym
        fields = [
            "id",
            "name",
            "contact_email",
            "contact_phone",
            "address",
            "equipments",
            "created_at",
            "updated_at",
        ]


class MobileTextContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileTextContent
        fields = ["id", "code", "group", "text", "created_at"]
        read_only_fields = ["id", "created_at"]
