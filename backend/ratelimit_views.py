from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

def too_many_requests(request, exception=None):
    logger.warning("⚠️ Rate limit hit!")
    return JsonResponse({"error": "Global rate limit exceeded."}, status=429)
