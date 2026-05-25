from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from gymApp.models import Subscription, SubscriptionPayment


@pytest.mark.django_db
@patch("gymApi.views.stripe.Webhook.construct_event")
def test_stripe_webhook_updates_subscription_status(
    mock_construct_event, user, api_client: APIClient
):
    subscription = Subscription.objects.create(
        user=user,
        stripe_customer_id="cus_123",
        stripe_subscription_id="sub_123",
        price_id="price_123",
        status="incomplete",
    )
    mock_construct_event.return_value = {
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": subscription.stripe_subscription_id,
                "status": "active",
                "items": {
                    "data": [
                        {
                            "created": 1,
                            "current_period_end": 1_710_000_000,
                        }
                    ]
                },
            }
        },
    }

    response = api_client.post(
        "/api/stripe_webhook/",
        data=b"{}",
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="sig",
    )

    subscription.refresh_from_db()

    assert response.status_code == 200
    assert subscription.status == "active"
    assert subscription.current_period_end is not None


@pytest.mark.django_db
@patch("gymApi.views.stripe.Webhook.construct_event")
def test_stripe_webhook_creates_subscription_payment(
    mock_construct_event, user, api_client: APIClient
):
    subscription = Subscription.objects.create(
        user=user,
        stripe_customer_id="cus_123",
        stripe_subscription_id="sub_123",
        price_id="price_123",
        status="active",
    )
    mock_construct_event.return_value = {
        "type": "invoice.paid",
        "data": {
            "object": {
                "id": "in_123",
                "subscription": subscription.stripe_subscription_id,
                "amount_paid": 1999,
                "currency": "usd",
                "created": 1_710_000_000,
            }
        },
    }

    response = api_client.post(
        "/api/stripe_webhook/",
        data=b"{}",
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="sig",
    )

    payment = SubscriptionPayment.objects.get(stripe_invoice_id="in_123")

    assert response.status_code == 200
    assert payment.subscription_id == subscription.id
    assert payment.amount_paid == 1999
    assert payment.currency == "usd"
