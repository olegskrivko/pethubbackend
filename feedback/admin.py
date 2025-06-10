from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('sender', 'email', 'get_subject_display', 'created_at', 'resolved', 'user')
    list_filter = ('subject', 'resolved', 'created_at')
    search_fields = ('sender', 'email', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def get_subject_display(self, obj):
        return dict(Feedback.SUBJECT_CHOICES).get(obj.subject, "Unknown")
    get_subject_display.short_description = 'Subject'
