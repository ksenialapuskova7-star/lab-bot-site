from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("django-admin/", admin.site.urls),   # встроенная (на всякий случай)
    path("admin/", include("bookings.admin_urls")),  # кастомная админка
    path("", include("bookings.urls")),
]