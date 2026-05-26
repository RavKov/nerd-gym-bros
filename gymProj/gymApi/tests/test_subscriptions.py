from unittest.mock import patch

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from gymApp.models import SubscriptionPlan


@pytest.mark.django_db
def test_subscription_plan_choose_updates_free_plan(
    authenticated_api_client: APIClient,
    client_profile,
):
    free_plan = SubscriptionPlan.objects.create(
        name="Free Plan",
        price=0,
        features="Free access",
    )

    response = authenticated_api_client.post(
        "/api/me/subscription_plan/choose/",
        {"subscription_plan_id": free_plan.id},
        format="json",
    )

    client_profile.refresh_from_db()

    assert response.status_code == 200
    assert client_profile.subscription_plan_id == free_plan.id


@pytest.mark.django_db
def test_subscription_plan_choose_rejects_paid_plan_without_stripe_flow(
    authenticated_api_client: APIClient,
    client_profile,
):
    original_plan_id = client_profile.subscription_plan_id
    paid_plan = SubscriptionPlan.objects.create(
        name="Paid Plan",
        price=19.99,
        stripe_price_id="price_123",
        features="Premium access",
    )

    response = authenticated_api_client.post(
        "/api/me/subscription_plan/choose/",
        {"subscription_plan_id": paid_plan.id},
        format="json",
    )

    client_profile.refresh_from_db()

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Paid subscription plans must be activated through Stripe payment flow."
    )
    assert client_profile.subscription_plan_id == original_plan_id


@pytest.mark.django_db
@override_settings(STRIPE_SECRET_KEY="sk_test_123")
def test_create_subscription_sheet_rejects_free_plan(
    authenticated_api_client: APIClient,
):
    free_plan = SubscriptionPlan.objects.create(
        name="Free Plan",
        price=0,
        features="Free access",
    )

    response = authenticated_api_client.post(
        "/api/create_subscription_sheet/",
        {"subscription_plan_id": free_plan.id},
        format="json",
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"] == "Selected subscription plan does not require Stripe payment."
    )


@pytest.mark.django_db
@override_settings(STRIPE_SECRET_KEY="sk_test_123")
@patch("gymApi.views.stripe.EphemeralKey.create")
@patch("gymApi.views.stripe.Subscription.create")
@patch("gymApi.views.stripe.Customer.create")
def test_create_subscription_sheet_uses_plan_lookup_for_paid_plan(
    mock_customer_create,
    mock_subscription_create,
    mock_ephemeral_key_create,
    authenticated_api_client: APIClient,
    client_profile,
):
    paid_plan = SubscriptionPlan.objects.create(
        name="Paid Plan",
        price=19.99,
        stripe_price_id="price_123",
        features="Premium access",
    )
    mock_customer_create.return_value = type("Customer", (), {"id": "cus_123"})()
    mock_subscription_create.return_value = type(
        "StripeSubscription",
        (),
        {
            "id": "sub_123",
            "status": "incomplete",
            "items": {"data": []},
            "cancel_at_period_end": False,
            "canceled_at": None,
            "ended_at": None,
            "latest_invoice": type(
                "LatestInvoice",
                (),
                {
                    "confirmation_secret": type(
                        "ConfirmationSecret",
                        (),
                        {"client_secret": "secret_123"},
                    )()
                },
            )(),
        },
    )()
    mock_ephemeral_key_create.return_value = type("EphemeralKey", (), {"secret": "ek_test"})()

    response = authenticated_api_client.post(
        "/api/create_subscription_sheet/",
        {"subscription_plan_id": paid_plan.id},
        format="json",
    )

    assert response.status_code == 200
    mock_subscription_create.assert_called_once()
    assert mock_subscription_create.call_args.kwargs["items"] == [
        {"price": paid_plan.stripe_price_id}
    ]
    assert response.json()["customerId"] == "cus_123"
    assert response.json()["clientSecret"] == "secret_123"
