from django.urls import path
from . import views

urlpatterns = [
    path("create-checkout-session/one-time/", views.create_one_time_payment_session, name="one-time-checkout"),
    path("create-checkout-session/subscription/", views.create_subscription_session, name="subscription-checkout"),
    path("webhook/", views.stripe_webhook, name="stripe-webhook"),
]
