from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    ButtonHolder,
    Column,
    Field,
    Fieldset,
    Layout,
    Row,
    Submit,
)
from django import forms
from django.forms import CheckboxSelectMultiple

from gymApp.models import Equipment, Exercise


class ExerciseForm(forms.ModelForm):
    equipments = forms.ModelMultipleChoiceField(
        queryset=Equipment.objects.all(),
        widget=CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "exercise_form"
        self.helper.form_method = "post"
        # self.helper.form_action = "add_exercise"
        self.helper.layout = Layout(
            Fieldset(
                "Exercise form",
                FloatingField("name"),
                FloatingField("description"),
                Row(
                    Column(FloatingField("difficulty_level")),
                    Column(FloatingField("exercise_type")),
                ),
                FloatingField("metabolic_equivalent"),
                FloatingField("amount_unit"),
                Field("equipments", css_class="text-start"),
                # PrependedText(
                #     "equipments", "Equipments (hold Ctrl to select multiple)"
                # ),
                Fieldset(
                    "Media",
                    Row(
                        Column(Field("video")),
                        Column(Field("thumbnail")),
                    ),
                    css_class="border p-3 mb-3",
                ),
                ButtonHolder(Submit("submit", "Save")),
                css_class="text-start",
            )
        )

    class Meta:
        model = Exercise

        fields = "__all__"
