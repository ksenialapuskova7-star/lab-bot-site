from django.urls import path
from . import admin_views as v

urlpatterns = [
    path("", v.admin_login, name="admin_login"),
    path("logout/", v.admin_logout, name="admin_logout"),
    path("panel/", v.admin_panel, name="admin_panel"),

    # Студенты
    path("students/", v.admin_students, name="admin_students"),
    path("students/add/", v.admin_student_add, name="admin_student_add"),
    path("students/<int:student_id>/delete/", v.admin_student_delete, name="admin_student_delete"),
    path("students/<int:student_id>/reset-password/", v.admin_student_reset_password, name="admin_student_reset_password"),

    # Предметы
    path("subjects/", v.admin_subjects, name="admin_subjects"),
    path("subjects/add/", v.admin_subject_add, name="admin_subject_add"),
    path("subjects/<int:subject_id>/", v.admin_subject_view, name="admin_subject_view"),
    path("subjects/<int:subject_id>/delete/", v.admin_subject_delete, name="admin_subject_delete"),
    path("subjects/<int:subject_id>/force-book/", v.admin_force_book, name="admin_force_book"),

    # Записи
    path("bookings/<int:booking_id>/delete/", v.admin_booking_delete, name="admin_booking_delete"),
]