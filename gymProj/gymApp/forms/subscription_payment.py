from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Column, Fieldset, Layout, Row, Submit
from django import forms

from gymApp.models import SubscriptionPayment


class SubscriptionPaymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "subscription_payment_form"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Fieldset(
                "Subscription Payment",
                FloatingField("stripe_invoice_id"),
                FloatingField("subscription"),
                Row(
                    Column(FloatingField("amount_paid")),
                    Column(FloatingField("currency")),
                ),
                FloatingField("paid_at"),
            ),
            ButtonHolder(Submit("submit", "Save")),
        )

    class Meta:
        model = SubscriptionPayment
        fields = [
            "stripe_invoice_id",
            "subscription",
            "amount_paid",
            "currency",
            "paid_at",
        ]
