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
from django.forms import CheckboxSelectMultiple

from gymApp.models import Gym, Address, Equipment


class GymForm(forms.ModelForm):
    street = forms.CharField(label="Street", max_length=255)
    city = forms.CharField(label="City", max_length=100)
    state = forms.CharField(label="State", max_length=100)
    postal_code = forms.CharField(label="Postal code", max_length=20)
    country = forms.CharField(label="Country", max_length=100)
    latitude = forms.DecimalField(
        label="Latitude", max_digits=9, decimal_places=6, required=False
    )
    longitude = forms.DecimalField(
        label="Longitude", max_digits=9, decimal_places=6, required=False
    )

    equipments = forms.ModelMultipleChoiceField(
        queryset=Equipment.objects.all(),
        widget=CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and getattr(self.instance, "address_id", None):
            address = self.instance.address
            self.initial.update(
                {
                    "street": address.street,
                    "city": address.city,
                    "state": address.state,
                    "postal_code": address.postal_code,
                    "country": address.country,
                    "latitude": address.latitude,
                    "longitude": address.longitude,
                }
            )

        self.helper = FormHelper()
        self.helper.form_id = "gym_form"
        self.helper.form_method = "post"

        self.helper.layout = Layout(
            Fieldset(
                "Gym details",
                FloatingField("name"),
                FloatingField("contact_email"),
                FloatingField("contact_phone"),
                Field("equipments", css_class="text-start"),
                css_class="text-start",
            ),
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
                css_class="text-start",
            ),
            ButtonHolder(Submit("submit", "Save")),
        )

    def save(self, commit=True):
        gym = super().save(commit=False)
        address_data = {
            "street": self.cleaned_data.get("street"),
            "city": self.cleaned_data.get("city"),
            "state": self.cleaned_data.get("state"),
            "postal_code": self.cleaned_data.get("postal_code"),
            "country": self.cleaned_data.get("country"),
            "latitude": self.cleaned_data.get("latitude"),
            "longitude": self.cleaned_data.get("longitude"),
        }

        if getattr(self.instance, "address_id", None):
            address = self.instance.address
            for field_name, value in address_data.items():
                setattr(address, field_name, value)
        else:
            address = Address(**address_data)

        if commit:
            address.save()
            gym.address = address
            gym.save()
            self.save_m2m()
        else:
            gym.address = address

        return gym

    class Meta:
        model = Gym
        fields = ["name", "contact_email", "contact_phone", "equipments"]
