"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings 
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/articles/', include('articles.urls')),
    path('api/auth/', include('authentication.urls')),
    path('api/chatbot/', include('chatbot.urls')),
    path('api/feedbacks/', include('feedback.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/pets/', include('pets.urls')),
    path('api/services/', include('services.urls')),
    path('api/shelters/', include('shelters.urls')),
]


# Serve media files in development
# Note:
# - There are **two main ways** to handle file uploads:
#   1. Using a cloud storage backend like Cloudinary via `django-cloudinary-storage`
#      - This replaces the need for serving files locally.
#   2. Manual uploads using Cloudinary API (gives more control over validation and logic).
# - This block is only necessary for **local development** when serving files via MEDIA_URL.
# - In production, file handling should be done via cloud services (Cloudinary, AWS S3, etc.)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)