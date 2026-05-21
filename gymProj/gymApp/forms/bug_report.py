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
from crispy_bootstrap5.bootstrap5 import FloatingField

from gymApp.models import BugReport


class BugReportForm(forms.ModelForm):
    resolved_at = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "bug_report_form"
        self.helper.form_method = "post"
        self.helper.form_enctype = "multipart/form-data"
        self.helper.layout = Layout(
            Fieldset(
                "Bug Report",
                FloatingField("user"),
                FloatingField("title"),
                FloatingField("description"),
                Field("screenshot"),
                Field("resolved"),
                Field("resolved_at"),
            ),
            ButtonHolder(Submit("submit", "Save")),
        )

    class Meta:
        model = BugReport
        fields = [
            "user",
            "title",
            "description",
            "screenshot",
            "resolved",
            "resolved_at",
        ]
