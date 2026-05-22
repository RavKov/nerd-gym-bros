from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Fieldset, Layout, Submit
from django import forms

from gymApp.models import Equipment


class EquipmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "equipment_form"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Fieldset(
                "Equipment",
                FloatingField("name"),
            ),
            ButtonHolder(Submit("submit", "Save")),
        )

    class Meta:
        model = Equipment
        fields = ["name"]
