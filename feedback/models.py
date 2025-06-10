from django.db import models
from django.conf import settings

class Feedback(models.Model):
    SUBJECT_CHOICES = [
        (1, 'Bug Report'),
        (2, 'General Questions'),
        (3, 'Feature Request'),
        (4, 'Collaboration Request'),
        (5, 'Other'),
    ]

    sender = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.PositiveSmallIntegerField(
        choices=SUBJECT_CHOICES,
        default=5,
        help_text="Select the subject of your feedback"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optional link to registered user"
    )
    resolved = models.BooleanField(default=False, help_text="Mark if feedback has been addressed")

    def __str__(self):
        subject_display = dict(self.SUBJECT_CHOICES).get(self.subject, "Unknown")
        return f"{self.sender} - {subject_display}"