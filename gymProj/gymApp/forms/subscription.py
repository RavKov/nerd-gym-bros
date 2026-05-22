from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    ButtonHolder,
    Field,
    Fieldset,
    Layout,
    Submit,
)
from django import forms
from django.forms import CheckboxSelectMultiple

from gymApp.models import (
    SubscriptionPlan,
    WorkoutPlan,
)


class SubscriptionPlanForm(forms.ModelForm):
    workout_plans = forms.ModelMultipleChoiceField(
        queryset=WorkoutPlan.objects.all(),
        widget=CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "subscription_plan_form"
        self.helper.form_method = "post"

        self.helper.layout = Layout(
            Fieldset(
                "Subscription Plan",
                FloatingField("name"),
                FloatingField("price"),
                FloatingField("duration_days"),
                Field("workout_plans", css_class="text-start"),
                # FloatingField(""),
                FloatingField("features"),
                ButtonHolder(Submit("submit", "Save")),
            ),
        )

    class Meta:
        model = SubscriptionPlan

        fields = "__all__"
