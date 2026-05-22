from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Fieldset, Layout, Submit
from django import forms


class LoginForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "login_form"
        self.helper.form_method = "post"
        self.helper.form_action = "login"
        self.helper.layout = Layout(
            Fieldset(
                "Login",
                FloatingField("username"),
                FloatingField("password"),
                ButtonHolder(Submit("submit", "Login")),
                css_class="text-center",
            )
        )
        # self.helper.add_input(Submit("submit", "Login"))

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"})
    )
