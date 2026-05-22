from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    ButtonHolder,
    Column,
    Fieldset,
    Layout,
    Row,
    Submit,
)
from django import forms

from gymApp.models import Address


class AddressForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "address_form"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Fieldset(
                "Address",
                FloatingField("street"),
                Row(
                    Column(FloatingField("city")),
                    Column(FloatingField("state")),
                ),
                Row(
                    Column(FloatingField("postal_code")),
                    Column(FloatingField("country")),
                ),
                Row(
                    Column(FloatingField("latitude")),
                    Column(FloatingField("longitude")),
                ),
            ),
            ButtonHolder(Submit("submit", "Save")),
        )

    class Meta:
        model = Address
        fields = "__all__"
