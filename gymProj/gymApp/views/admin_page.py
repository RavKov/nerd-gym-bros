import json
from datetime import date
from decimal import Decimal
from logging import getLogger

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from gymApp.forms import (
    BugReportForm,
    EquipmentForm,
    ExerciseForm,
    ExerciseTypeForm,
    GymForm,
    LoginForm,
    NewFeatureRequestForm,
    StaffForm,
    SubscriptionPaymentForm,
    SubscriptionPlanForm,
    UpdateStaffForm,
    WorkoutDayForm,
    WorkoutItemForm,
    WorkoutPlanForm,
)
from gymApp.models import (
    BugReport,
    ClientProfile,
    Equipment,
    Exercise,
    ExerciseType,
    Gym,
    NewFeatureRequest,
    Subscription,
    SubscriptionPayment,
    SubscriptionPlan,
    WorkoutDay,
    WorkoutItem,
    WorkoutPlan,
)

log = getLogger(__name__)

from django.core.mail import send_mail
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)


class ExerciseListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Exercise
    template_name = "gymApp/exercise/list.html"
    context_object_name = "exercises"
    permission_required = "gymApp.view_exercise"
    raise_exception = True


class ExerciseCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Exercise
    template_name = "gymApp/exercise/form.html"
    success_url = reverse_lazy("exercise_list")
    form_class = ExerciseForm
    permission_required = "gymApp.add_exercise"
    raise_exception = True


class ExerciseUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Exercise
    template_name = "gymApp/exercise/form.html"
    success_url = reverse_lazy("exercise_list")
    form_class = ExerciseForm
    permission_required = "gymApp.change_exercise"
    raise_exception = True


class ExerciseDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Exercise
    template_name = "gymApp/exercise/detail.html"
    context_object_name = "exercise"
    permission_required = "gymApp.view_exercise"
    raise_exception = True


class ExerciseDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Exercise
    template_name = "gymApp/exercise/confirm_delete.html"
    context_object_name = "exercise"
    success_url = reverse_lazy("exercise_list")
    permission_required = "gymApp.delete_exercise"
    raise_exception = True


class GymListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Gym
    template_name = "gymApp/gym/list.html"
    context_object_name = "gyms"
    permission_required = "gymApp.view_gym"
    raise_exception = True


class GymCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Gym
    template_name = "gymApp/gym/form.html"
    success_url = reverse_lazy("gym_list")
    form_class = GymForm
    permission_required = "gymApp.add_gym"
    raise_exception = True


class GymUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Gym
    template_name = "gymApp/gym/form.html"
    success_url = reverse_lazy("gym_list")
    form_class = GymForm
    permission_required = "gymApp.change_gym"
    raise_exception = True


class GymDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Gym
    template_name = "gymApp/gym/detail.html"
    context_object_name = "gym"
    permission_required = "gymApp.view_gym"
    raise_exception = True


class GymDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Gym
    template_name = "gymApp/gym/confirm_delete.html"
    context_object_name = "gym"
    success_url = reverse_lazy("gym_list")
    permission_required = "gymApp.delete_gym"
    raise_exception = True


class BugReportListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = BugReport
    template_name = "gymApp/bug_report/list.html"
    context_object_name = "bug_reports"
    permission_required = "gymApp.view_bugreport"
    raise_exception = True


class BugReportCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = BugReport
    template_name = "gymApp/bug_report/form.html"
    success_url = reverse_lazy("bug_report_list")
    form_class = BugReportForm
    permission_required = "gymApp.add_bugreport"
    raise_exception = True


class BugReportUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = BugReport
    template_name = "gymApp/bug_report/form.html"
    success_url = reverse_lazy("bug_report_list")
    form_class = BugReportForm
    permission_required = "gymApp.change_bugreport"
    raise_exception = True


class BugReportDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = BugReport
    template_name = "gymApp/bug_report/detail.html"
    context_object_name = "bug_report"
    permission_required = "gymApp.view_bugreport"
    raise_exception = True


class BugReportDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = BugReport
    template_name = "gymApp/bug_report/confirm_delete.html"
    context_object_name = "bug_report"
    success_url = reverse_lazy("bug_report_list")
    permission_required = "gymApp.delete_bugreport"
    raise_exception = True


class NewFeatureRequestListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = NewFeatureRequest
    template_name = "gymApp/new_feature_request/list.html"
    context_object_name = "feature_requests"
    permission_required = "gymApp.view_newfeaturerequest"
    raise_exception = True


class NewFeatureRequestCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = NewFeatureRequest
    template_name = "gymApp/new_feature_request/form.html"
    success_url = reverse_lazy("new_feature_request_list")
    form_class = NewFeatureRequestForm
    permission_required = "gymApp.add_newfeaturerequest"
    raise_exception = True


class NewFeatureRequestUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = NewFeatureRequest
    template_name = "gymApp/new_feature_request/form.html"
    success_url = reverse_lazy("new_feature_request_list")
    form_class = NewFeatureRequestForm
    permission_required = "gymApp.change_newfeaturerequest"
    raise_exception = True


class NewFeatureRequestDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = NewFeatureRequest
    template_name = "gymApp/new_feature_request/detail.html"
    context_object_name = "feature_request"
    permission_required = "gymApp.view_newfeaturerequest"
    raise_exception = True


class NewFeatureRequestDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = NewFeatureRequest
    template_name = "gymApp/new_feature_request/confirm_delete.html"
    context_object_name = "feature_request"
    success_url = reverse_lazy("new_feature_request_list")
    permission_required = "gymApp.delete_newfeaturerequest"
    raise_exception = True


class EquipmentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Equipment
    template_name = "gymApp/equipment/list.html"
    context_object_name = "equipments"
    permission_required = "gymApp.view_equipment"
    raise_exception = True


class EquipmentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Equipment
    template_name = "gymApp/equipment/form.html"
    success_url = reverse_lazy("equipment_list")
    form_class = EquipmentForm
    permission_required = "gymApp.add_equipment"
    raise_exception = True


class EquipmentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Equipment
    template_name = "gymApp/equipment/form.html"
    success_url = reverse_lazy("equipment_list")
    form_class = EquipmentForm
    permission_required = "gymApp.change_equipment"
    raise_exception = True


class EquipmentDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Equipment
    template_name = "gymApp/equipment/detail.html"
    context_object_name = "equipment"
    permission_required = "gymApp.view_equipment"
    raise_exception = True


class EquipmentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Equipment
    template_name = "gymApp/equipment/confirm_delete.html"
    context_object_name = "equipment"
    success_url = reverse_lazy("equipment_list")
    permission_required = "gymApp.delete_equipment"
    raise_exception = True


class ExerciseTypeListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = ExerciseType
    template_name = "gymApp/exercise_type/list.html"
    context_object_name = "exercise_types"
    permission_required = "gymApp.view_exercisetype"
    raise_exception = True


class ExerciseTypeCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = ExerciseType
    template_name = "gymApp/exercise_type/form.html"
    success_url = reverse_lazy("exercise_type_list")
    form_class = ExerciseTypeForm
    permission_required = "gymApp.add_exercisetype"
    raise_exception = True


class ExerciseTypeUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = ExerciseType
    template_name = "gymApp/exercise_type/form.html"
    success_url = reverse_lazy("exercise_type_list")
    form_class = ExerciseTypeForm
    permission_required = "gymApp.change_exercisetype"
    raise_exception = True


class ExerciseTypeDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = ExerciseType
    template_name = "gymApp/exercise_type/detail.html"
    context_object_name = "exercise_type"
    permission_required = "gymApp.view_exercisetype"
    raise_exception = True


class ExerciseTypeDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = ExerciseType
    template_name = "gymApp/exercise_type/confirm_delete.html"
    context_object_name = "exercise_type"
    success_url = reverse_lazy("exercise_type_list")
    permission_required = "gymApp.delete_exercisetype"
    raise_exception = True


class SubscriptionPaymentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = SubscriptionPayment
    template_name = "gymApp/subscription_payment/list.html"
    context_object_name = "subscription_payments"
    permission_required = "gymApp.view_subscriptionpayment"
    raise_exception = True


class SubscriptionPaymentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = SubscriptionPayment
    template_name = "gymApp/subscription_payment/form.html"
    success_url = reverse_lazy("subscription_payment_list")
    form_class = SubscriptionPaymentForm
    permission_required = "gymApp.add_subscriptionpayment"
    raise_exception = True


class SubscriptionPaymentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = SubscriptionPayment
    template_name = "gymApp/subscription_payment/form.html"
    success_url = reverse_lazy("subscription_payment_list")
    form_class = SubscriptionPaymentForm
    permission_required = "gymApp.change_subscriptionpayment"
    raise_exception = True


class SubscriptionPaymentDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = SubscriptionPayment
    template_name = "gymApp/subscription_payment/detail.html"
    context_object_name = "subscription_payment"
    permission_required = "gymApp.view_subscriptionpayment"
    raise_exception = True


class WorkoutPlanListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = WorkoutPlan
    template_name = "gymApp/workout_plan/list.html"
    context_object_name = "workout_plans"
    permission_required = "gymApp.view_workoutplan"
    raise_exception = True


class WorkoutPlanDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = WorkoutPlan
    template_name = "gymApp/workout_plan/detail.html"
    context_object_name = "workout_plan"
    permission_required = "gymApp.view_workoutplan"
    raise_exception = True


class WorkoutPlanCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = WorkoutPlan
    template_name = "gymApp/workout_plan/form.html"
    form_class = WorkoutPlanForm
    permission_required = "gymApp.add_workoutplan"
    raise_exception = True

    def get_success_url(self):
        return reverse("workout_plan_update", kwargs={"pk": self.object.pk})


class WorkoutPlanUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = WorkoutPlan
    template_name = "gymApp/workout_plan/form.html"
    success_url = reverse_lazy("workout_plan_list")
    fields = "__all__"
    permission_required = "gymApp.change_workoutplan"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = WorkoutPlanForm(instance=self.object)
        context["workout_days"] = WorkoutDay.objects.filter(workout_plan=self.object)
        return context


class WorkoutPlanDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = WorkoutPlan
    template_name = "gymApp/workout_plan/confirm_delete.html"
    context_object_name = "workout_plan"
    success_url = reverse_lazy("workout_plan_list")
    permission_required = "gymApp.delete_workoutplan"
    raise_exception = True


class SubscriptionPlanListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = SubscriptionPlan
    template_name = "gymApp/subscription_plan/list.html"
    context_object_name = "subscription_plans"
    permission_required = "gymApp.view_subscriptionplan"


class SubscriptionPlanCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = SubscriptionPlan
    template_name = "gymApp/subscription_plan/form.html"
    success_url = reverse_lazy("subscription_plan_list")
    form_class = SubscriptionPlanForm
    permission_required = "gymApp.add_subscriptionplan"
    raise_exception = True


class SubscriptionPlanUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = SubscriptionPlan
    template_name = "gymApp/subscription_plan/form.html"
    success_url = reverse_lazy("subscription_plan_list")
    form_class = SubscriptionPlanForm
    permission_required = "gymApp.change_subscriptionplan"
    raise_exception = True


class SubscriptionPlanDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = SubscriptionPlan
    template_name = "gymApp/subscription_plan/confirm_delete.html"
    context_object_name = "subscription_plan"
    success_url = reverse_lazy("subscription_plan_list")
    permission_required = "gymApp.delete_subscriptionplan"
    raise_exception = True


class StaffListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = "gymApp/staff/list.html"
    context_object_name = "staff_members"

    def get_queryset(self):
        return User.objects.filter(is_staff=True)

    def test_func(self):
        """Only superusers can view staff accounts."""
        return self.request.user.is_superuser


class StaffCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = User
    template_name = "gymApp/staff/form.html"
    success_url = reverse_lazy("staff_list")
    form_class = StaffForm

    def test_func(self):
        """Only superusers can create staff accounts."""
        return self.request.user.is_superuser

    def form_valid(self, form):
        user: User = form.save(commit=False)
        user.is_staff = True
        user.save()
        form.save_m2m()  # Save many-to-many relationships (groups)

        self.object = user

        try:
            send_mail(
                subject="Your staff account was created",
                message=(
                    f"Hello {user.get_full_name() or user.username},\n\n"
                    "A staff account was created for you. "
                    "Contact your administrator to receive login credentials securely.\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            messages.success(
                self.request,
                "Staff account created. Share login credentials through a secure channel "
                "(password is not sent by email).",
            )
        except Exception as e:
            messages.warning(self.request, f"Staff account created, but email failed: {e}")

        return redirect(self.get_success_url())


class StaffUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    template_name = "gymApp/staff/update_form.html"
    success_url = reverse_lazy("staff_list")
    form_class = UpdateStaffForm
    context_object_name = "staff_member"

    def test_func(self):
        """Only superusers can update staff accounts."""
        return self.request.user.is_superuser

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["form"] = UpdateStaffForm(instance=self.object)
    #     return context


class StaffDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = "gymApp/staff/confirm_delete.html"
    context_object_name = "staff_member"
    success_url = reverse_lazy("staff_list")

    def test_func(self):
        """Only superusers can delete staff accounts."""
        return self.request.user.is_superuser


class ClientListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = ClientProfile
    template_name = "gymApp/client/list.html"
    context_object_name = "clients"
    permission_required = "gymApp.view_clientprofile"
    raise_exception = True


class ClientToggleActiveView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = ClientProfile
    fields = []
    template_name = "gymApp/client/confirm_toggle_active.html"
    context_object_name = "client"
    success_url = reverse_lazy("client_list")
    permission_required = "gymApp.change_clientprofile"
    raise_exception = True

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = self.object.user
        user.is_active = not user.is_active
        user.save()
        return redirect(self.get_success_url())


@login_required
def reports_view(request: HttpRequest):
    from gymReports.views import ensure_default_templates, get_report_catalog

    ensure_default_templates()
    return render(
        request,
        "gymApp/reports.html",
        {"report_categories": get_report_catalog()},
    )


def workout_day_create_view(request: HttpRequest):
    if request.method == "POST":
        form = WorkoutDayForm(request.POST)
        if form.is_valid():
            workout_day = WorkoutDay.create_at_end(**form.cleaned_data)

            return redirect("workout_day_update", pk=workout_day.pk)
    form = WorkoutDayForm(initial={"workout_plan": request.GET.get("workout_plan")})
    return render(
        request,
        "gymApp/workout_day/form.html",
        {"form": form, "workout_items": []},
    )


def workout_day_update_view(request: HttpRequest, pk: int):
    workout_day = get_object_or_404(WorkoutDay, pk=pk)

    if request.method == "POST":
        form = WorkoutDayForm(request.POST, instance=workout_day)
        if form.is_valid():
            workout_day = form.save()
            return redirect("workout_day_update", pk=workout_day.pk)

    workout_items = WorkoutItem.objects.filter(workout_day=workout_day)
    form = WorkoutDayForm(instance=workout_day)
    return render(
        request,
        "gymApp/workout_day/form.html",
        {
            "form": form,
            "workout_items": workout_items,
            "workout_item_form": WorkoutItemForm(initial={"workout_day": workout_day}),
        },
    )


def workout_day_delete_view(request: HttpRequest, pk: int):
    if request.method == "POST":
        try:
            day = WorkoutDay.objects.get(id=pk)
            workout_plan_id = day.workout_plan.pk
            day.delete()
            return redirect("workout_plan_update", pk=workout_plan_id)
        except WorkoutDay.DoesNotExist:
            return HttpResponse("Workout day not found.", status=404)
    return HttpResponse("Invalid request method.", status=400)


def workout_item_create_view(request: HttpRequest):
    print(request.method == "POST")
    if request.method == "POST":
        form = WorkoutItemForm(request.POST)
        # form.fields["workout_plan"].widget = form.fields[
        print(f"FORM: {form.errors=}")
        if form.is_valid():
            print(form.cleaned_data)
            workout_item = WorkoutItem.create_at_end(**form.cleaned_data)
            # workout_item = form.save()
            return redirect("workout_day_update", pk=workout_item.workout_day.pk)
    return HttpResponse("Invalid request method.", status=400)


def workout_item_delete_view(request: HttpRequest, pk: int):
    if request.method == "POST":
        try:
            item = WorkoutItem.objects.get(id=pk)
            workout_day_id = item.workout_day.pk
            item.delete()
            return redirect("workout_day_update", pk=workout_day_id)
        except WorkoutItem.DoesNotExist:
            return HttpResponse("Workout item not found.", status=404)
    return HttpResponse("Invalid request method.", status=400)


def workout_item_reorder_view(request: HttpRequest):
    if request.method == "POST":
        jsonData = json.loads(request.body.decode("utf-8"))

        with transaction.atomic():
            bump = 100000
            # This avoids unique constraint violation
            for item in jsonData:
                WorkoutItem.objects.filter(pk=item["id"]).update(order=int(item["order"]) + bump)

            for item in jsonData:
                WorkoutItem.objects.filter(pk=item["id"]).update(order=int(item["order"]))
        return HttpResponse("Workout items reordered successfully.", status=200)


def workout_day_reorder_view(request: HttpRequest):
    if request.method == "POST":
        jsonData = json.loads(request.body.decode("utf-8"))

        with transaction.atomic():
            bump = 100000
            # This avoids unique constraint violation
            for item in jsonData:
                WorkoutDay.objects.filter(pk=item["id"]).update(
                    day_number=int(item["day_number"]) + bump
                )

            for item in jsonData:
                WorkoutDay.objects.filter(pk=item["id"]).update(day_number=int(item["day_number"]))
        return HttpResponse("Workout days reordered successfully.", status=200)


POST = "POST"


def login_view(request: HttpRequest):
    error = ""
    if request.method == POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                redirect_to_home = request.POST.get("next", "/")
                return redirect(redirect_to_home)
        error = "Invalid username or password."

    form = LoginForm(request.POST or None)
    if error:
        form.add_error(None, error)

    return render(request, "gymApp/login.html", {"error": error, "form": form})


def logout_view(request: HttpRequest):
    if request.user:
        logout(request)
    return redirect("login")


@login_required
def home_view(request: HttpRequest):
    month_count = 6
    today = timezone.now().date()

    def month_starts(count: int, end_date: date) -> list[date]:
        starts: list[date] = []
        year = end_date.year
        month = end_date.month
        for offset in range(count - 1, -1, -1):
            y = year
            m = month - offset
            while m <= 0:
                m += 12
                y -= 1
            starts.append(date(y, m, 1))
        return starts

    months = month_starts(month_count, today)
    month_labels = [m.strftime("%b %Y") for m in months]
    month_start = months[0]

    bug_report_qs = (
        BugReport.objects.filter(created_at__date__gte=month_start)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Count("id"))
    )
    feature_request_qs = (
        NewFeatureRequest.objects.filter(created_at__date__gte=month_start)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Count("id"))
    )
    subscription_qs = (
        Subscription.objects.filter(created_at__date__gte=month_start)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Count("id"))
    )
    payment_qs = (
        SubscriptionPayment.objects.filter(paid_at__date__gte=month_start)
        .annotate(month=TruncMonth("paid_at"))
        .values("month")
        .annotate(total=Sum("amount_paid"))
    )

    def map_month_values(qs) -> dict[date, int]:
        return {item["month"].date(): int(item["total"] or 0) for item in qs if item["month"]}

    bug_map = map_month_values(bug_report_qs)
    feature_map = map_month_values(feature_request_qs)
    subscription_map = map_month_values(subscription_qs)
    payment_map = {
        item["month"].date(): Decimal(item["total"] or 0) / Decimal("100")
        for item in payment_qs
        if item["month"]
    }

    bug_series = [bug_map.get(m, 0) for m in months]
    feature_series = [feature_map.get(m, 0) for m in months]
    subscription_series = [subscription_map.get(m, 0) for m in months]
    payment_series = [float(payment_map.get(m, Decimal("0"))) for m in months]

    subscription_status = (
        Subscription.objects.values("status").annotate(total=Count("id")).order_by("status")
    )
    status_labels = [item["status"] for item in subscription_status]
    status_values = [item["total"] for item in subscription_status]

    context = {
        "stats": {
            "gyms": Gym.objects.count(),
            "clients": ClientProfile.objects.count(),
            "exercises": Exercise.objects.count(),
            "workout_plans": WorkoutPlan.objects.count(),
            "subscriptions": Subscription.objects.count(),
            "active_subscriptions": Subscription.objects.filter(status="active").count(),
            "payments": SubscriptionPayment.objects.count(),
            "bug_reports": BugReport.objects.count(),
            "feature_requests": NewFeatureRequest.objects.count(),
        },
        "month_labels": month_labels,
        "bug_series": bug_series,
        "feature_series": feature_series,
        "subscription_series": subscription_series,
        "payment_series": payment_series,
        "status_labels": status_labels,
        "status_values": status_values,
    }
    return render(request, "gymApp/home.html", context)


@login_required
def add_exercise_view(request: HttpRequest):
    errors = {}
    if request.method == POST:
        form = ExerciseForm(request.POST, request.FILES)
        if form.is_valid():
            ex = form.save(commit=False)
            ex.save()
            return redirect("home")
        errors = form.errors
    else:
        form = ExerciseForm()

    return render(request, "gymApp/add_exercise.html", {"form": form, "errors": errors})
