from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


def too_many_requests(request, exception=None):
    """
    Handle rate limit exceeded requests.
    
    Args:
        request: The HTTP request object
        exception: The rate limit exception (optional)
        
    Returns:
        JsonResponse: Error response with 429 status code
    """
    logger.warning("Rate limit exceeded for request")
    return JsonResponse({"error": "Global rate limit exceeded."}, status=429)
