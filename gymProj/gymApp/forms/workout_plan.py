from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    ButtonHolder,
    Fieldset,
    Layout,
    Submit,
)
from django import forms

from gymApp.models import (
    WorkoutPlan,
)


class WorkoutPlanForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "workout_plan_form"
        self.helper.form_method = "post"
        # self.helper.form_action = "add_workout_plan"
        self.helper.layout = Layout(
            Fieldset(
                "Workout Plan form",
                FloatingField("name"),
                FloatingField("description"),
                FloatingField("difficulty_level"),
                ButtonHolder(Submit("submit", "Save")),
            ),
        )

    class Meta:
        model = WorkoutPlan

        fields = "__all__"
