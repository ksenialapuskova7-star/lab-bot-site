from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("subjects/", views.subjects, name="subjects"),
    path("subjects/<int:subject_id>/", views.subject_detail, name="subject_detail"),
    path("subjects/<int:subject_id>/book/", views.book_slot, name="book_slot"),

    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("my-bookings/<int:booking_id>/cancel/", views.cancel_booking, name="cancel_booking"),
]