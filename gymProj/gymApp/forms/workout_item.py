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

from gymApp.models import (
    WorkoutItem,
)


class WorkoutItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "workout_item_form"
        self.helper.form_method = "post"
        self.helper.form_action = "workout_item_create"

        self.helper.layout = Layout(
            Fieldset(
                "Workout Item form",
                FloatingField("exercise"),
                FloatingField("sets"),
                FloatingField("amount"),
                # FloatingField("order"),
                Field("workout_day", type="hidden"),
                ButtonHolder(Submit("submit", "Save")),
            ),
        )

    class Meta:
        model = WorkoutItem
        exclude = ("order",)
        fields = "__all__"
