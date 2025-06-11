from django.urls import path
from . import views

urlpatterns = [
    path("create-checkout-session/one-time/", views.create_one_time_payment_session, name="one-time-checkout"),
    path("create-checkout-session/subscription/", views.create_subscription_session, name="subscription-checkout"),
    path("webhook/", views.stripe_webhook, name="stripe-webhook"),
    
    # New subscription management endpoints
    path("subscription/status/", views.get_subscription_status, name="subscription-status"),
    path("subscription/cancel/", views.cancel_subscription, name="cancel-subscription"),
    # path("subscription/reactivate/", views.reactivate_subscription, name="reactivate-subscription"),
    #path("subscription/history/", views.get_subscription_history, name="subscription-history"),
]
