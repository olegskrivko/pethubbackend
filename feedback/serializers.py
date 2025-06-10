from rest_framework import serializers
from .models import Feedback
import re

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = "__all__"

    def validate_sender(self, value):
        if not value.strip():
            raise serializers.ValidationError("Lūdzu, ievadiet savu vārdu.")
        if len(value) < 2:
            raise serializers.ValidationError("Vārds ir pārāk īss.")
        if any(char.isdigit() for char in value):
            raise serializers.ValidationError("Vārds nedrīkst saturēt ciparus.")
        return value

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Lūdzu, ievadiet e-pastu.")
        # Extra: basic domain pattern check
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise serializers.ValidationError("Lūdzu, ievadiet derīgu e-pastu.")
        return value

    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("Ziņa nedrīkst būt tukša.")
        if len(value) > 500:
            raise serializers.ValidationError("Ziņa nedrīkst pārsniegt 500 rakstzīmes.")
        if len(value) < 3:
            raise serializers.ValidationError("Ziņa ir pārāk īsa.")
        return value

    def validate(self, data):
        """
        Global validation if needed (e.g. avoid same email & message repeated).
        """
        if Feedback.objects.filter(email=data['email'], message=data['message']).exists():
            raise serializers.ValidationError("Šī ziņa jau ir nosūtīta no šī e-pasta.")
        return data
