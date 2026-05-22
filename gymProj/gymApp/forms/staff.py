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
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.forms import CheckboxSelectMultiple


class StaffForm(UserCreationForm):
    # is_superuser = forms.BooleanField(required=False, label="Admin Status")
    # is_active = forms.BooleanField(required=False, label="Active")

    # date_joined = forms.DateField(
    #     initial=timezone.localdate(),
    #     widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    #     label="Select a Date",
    # )

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "staff_form"
        self.helper.form_method = "post"

        # date_joined_field = self.fields.get("date_joined")
        # if date_joined_field:
        #     date_joined_field.widget.attrs["readonly"] = True

        self.helper.layout = Layout(
            Fieldset(
                "Staff Member",
                FloatingField("username"),
                FloatingField("email"),
                FloatingField("first_name"),
                FloatingField("last_name"),
                FloatingField("password1"),
                FloatingField("password2"),
                FloatingField("date_joined"),
                Field("is_superuser"),
                Field("is_active"),
                Field("groups"),
                ButtonHolder(Submit("submit", "Save")),
            ),
        )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "date_joined",
            "is_active",
            "is_superuser",
            "groups",
        )
