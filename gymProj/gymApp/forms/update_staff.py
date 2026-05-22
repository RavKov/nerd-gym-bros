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
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import Group, User
from django.forms import CheckboxSelectMultiple


class UpdateStaffForm(UserChangeForm):
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

        self.helper.layout = Layout(
            Fieldset(
                "Staff Member",
                FloatingField("username"),
                FloatingField("email"),
                FloatingField("first_name"),
                FloatingField("last_name"),
                Field("is_superuser"),
                Field("is_active"),
                Field("groups"),
                ButtonHolder(Submit("submit", "Save")),
            ),
        )

    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_superuser",
            "groups",
        )
