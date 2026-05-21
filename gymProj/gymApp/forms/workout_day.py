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
from django.db.models import Max  # <-- add

from django.forms import CheckboxSelectMultiple, CheckboxSelectMultiple
from crispy_forms.bootstrap import PrependedText
from crispy_bootstrap5.bootstrap5 import FloatingField
from gymApp.models import (
    Exercise,
    DifficultyLevel,
    ExerciseType,
    Equipment,
    WorkoutDay,
    WorkoutPlan,
)


class WorkoutDayForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_order()

        self.helper = FormHelper()
        self.helper.form_id = "workout_day_form"
        self.helper.form_method = "post"
        # self.helper.form_action = "add_workout_plan"
        self.helper.layout = Layout(
            Fieldset(
                "Workout Day {{ form.instance.day_number|default:'' }} ",
                FloatingField("description"),
                Field("day_number", type="hidden"),
                Field("workout_plan", type="hidden"),
                ButtonHolder(Submit("submit", "Save")),
            ),
        )

    def set_order(self):
        if not self.instance.pk:
            wp = self.initial.get("workout_plan")
            if wp:
                max_day = (
                    WorkoutDay.objects.filter(workout_plan_id=wp).aggregate(
                        Max("day_number")
                    )["day_number__max"]
                    or 0
                )
                self.fields["day_number"].initial = max_day + 1
            else:
                self.fields["day_number"].initial = 1
        else:
            self.fields["day_number"].initial = self.instance.day_number

    class Meta:
        model = WorkoutDay

        fields = "__all__"
