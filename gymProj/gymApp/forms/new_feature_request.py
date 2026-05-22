from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    ButtonHolder,
    Fieldset,
    Layout,
    Submit,
)
from django import forms

from gymApp.models import NewFeatureRequest


class NewFeatureRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "new_feature_request_form"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Fieldset(
                "New Feature Request",
                FloatingField("user"),
                FloatingField("title"),
                FloatingField("description"),
                FloatingField("status"),
            ),
            ButtonHolder(Submit("submit", "Save")),
        )

    class Meta:
        model = NewFeatureRequest
        fields = ["user", "title", "description", "status"]
