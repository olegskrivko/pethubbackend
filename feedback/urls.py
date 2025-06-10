from django.urls import path
from .views import FeedbackCreateView

urlpatterns = [
    path('', FeedbackCreateView.as_view(), name='send-feedback'),
]
