from django import forms
from gymReports.models import PrintTemplate


class PrintTemplateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["report_key"].widget.attrs.update({"class": "form-select"})
        self.fields["name"].widget.attrs.update({"class": "form-control"})
        self.fields["template_file"].widget.attrs.update({"class": "form-control"})
        self.fields["is_active"].widget.attrs.update({"class": "form-check-input"})

    class Meta:
        model = PrintTemplate
        fields = ["report_key", "name", "template_file", "is_active"]
