from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from crispy_bootstrap5.bootstrap5 import FloatingField

from gymApp.models import ExerciseType


class ExerciseTypeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "exercise_type_form"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Fieldset(
                "Exercise Type",
                FloatingField("name"),
            ),
            ButtonHolder(Submit("submit", "Save")),
        )

    class Meta:
        model = ExerciseType
        fields = ["name"]
