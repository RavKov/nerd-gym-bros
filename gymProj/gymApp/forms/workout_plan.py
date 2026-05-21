from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Submit,
    Layout,
    Fieldset,
    ButtonHolder,
    Row,
    Column,
    Field,
)
from django.forms import CheckboxSelectMultiple, CheckboxSelectMultiple
from crispy_forms.bootstrap import PrependedText
from crispy_bootstrap5.bootstrap5 import FloatingField
from gymApp.models import (
    Exercise,
    DifficultyLevel,
    ExerciseType,
    Equipment,
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
