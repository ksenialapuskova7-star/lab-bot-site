from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect, get_object_or_404

from .forms import AdminLoginForm, StudentAddForm, SubjectForm, ForceBookForm
from .models import Student, Subject, Booking


# ============ ДЕКОРАТОР ПРОВЕРКИ АДМИНА ============

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("is_admin"):
            return redirect("admin_login")
        return view_func(request, *args, **kwargs)
    return wrapper


# ============ ВХОД ============

def admin_login(request):
    if request.session.get("is_admin"):
        return redirect("admin_panel")

    if request.method == "POST":
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["password"] == settings.ADMIN_PASSWORD:
                request.session["is_admin"] = True
                return redirect("admin_panel")
            messages.error(request, "Неверный пароль.")
    else:
        form = AdminLoginForm()

    return render(request, "admin/login.html", {"form": form})


def admin_logout(request):
    request.session.pop("is_admin", None)
    return redirect("admin_login")


# ============ ПАНЕЛЬ ============

@admin_required
def admin_panel(request):
    stats = {
        "students_total": Student.objects.count(),
        "students_registered": Student.objects.filter(is_registered=True).count(),
        "subjects_total": Subject.objects.filter(is_active=True).count(),
        "bookings_total": Booking.objects.count(),
    }
    return render(request, "admin/panel.html", {"stats": stats})


# ============ СТУДЕНТЫ ============

@admin_required
def admin_students(request):
    students = Student.objects.all().order_by("group_name", "last_name", "first_name")
    return render(request, "admin/students.html", {"students": students})


@admin_required
def admin_student_add(request):
    if request.method == "POST":
        form = StudentAddForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Студент добавлен в список.")
            return redirect("admin_students")
    else:
        form = StudentAddForm()
    return render(request, "admin/student_add.html", {"form": form})


@admin_required
def admin_student_delete(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        if student.user:
            student.user.delete()  # каскадно удалит Student и Booking
        else:
            student.delete()
        messages.success(request, "Студент удалён.")
        return redirect("admin_students")
    return render(request, "admin/confirm_delete.html", {
        "title": "Удалить студента?",
        "object": student,
        "cancel_url": "admin_students",
    })


@admin_required
def admin_student_reset_password(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        if student.user:
            student.user.delete()
            student.user = None
            student.is_registered = False
            student.save()
            messages.success(request, f"Пароль {student.full_name} сброшен. Теперь он может зарегистрироваться заново.")
        else:
            messages.warning(request, "Студент ещё не зарегистрирован.")
        return redirect("admin_students")
    return render(request, "admin/confirm_action.html", {
        "title": "Сбросить пароль?",
        "message": f"Студент {student.full_name} сможет зарегистрироваться заново. Все его записи на предметы будут удалены.",
        "cancel_url": "admin_students",
    })


# ============ ПРЕДМЕТЫ ============

@admin_required
def admin_subjects(request):
    subjects = Subject.objects.filter(is_active=True).order_by("date", "start_time")
    return render(request, "admin/subjects.html", {"subjects": subjects})


@admin_required
def admin_subject_add(request):
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Предмет добавлен.")
            return redirect("admin_subjects")
    else:
        form = SubjectForm()
    return render(request, "admin/subject_add.html", {"form": form})


@admin_required
def admin_subject_delete(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if request.method == "POST":
        subject.is_active = False
        subject.save()
        messages.success(request, "Предмет удалён.")
        return redirect("admin_subjects")
    return render(request, "admin/confirm_delete.html", {
        "title": "Удалить предмет?",
        "object": subject,
        "cancel_url": "admin_subjects",
    })


@admin_required
def admin_subject_view(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    booked_slots = set(subject.bookings.values_list("slot_number", flat=True))

    slots = []
    for i in range(1, subject.max_slots + 1):
        booking = subject.bookings.filter(slot_number=i).first()
        slots.append({
            "number": i,
            "booking": booking,
        })

    return render(request, "admin/subject_view.html", {
        "subject": subject,
        "slots": slots,
        "booked_slots": booked_slots,
    })


# ============ ПРИНУДИТЕЛЬНАЯ ЗАПИСЬ ============

@admin_required
def admin_force_book(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)

    if request.method == "POST":
        form = ForceBookForm(request.POST, subject=subject)
        if form.is_valid():
            student_id = form.cleaned_data["student_id"]
            slot_number = int(form.cleaned_data["slot_number"])
            student = get_object_or_404(Student, id=student_id)

            try:
                with transaction.atomic():
                    Booking.objects.create(
                        subject=subject,
                        slot_number=slot_number,
                        student=student,
                        last_name=student.last_name,
                    )
                messages.success(request, f"{student.full_name} записан на место {slot_number}.")
                return redirect("admin_subject_view", subject_id=subject.id)
            except IntegrityError:
                messages.error(request, "Место занято или студент уже записан.")
    else:
        form = ForceBookForm(subject=subject)

    return render(request, "admin/force_book.html", {"form": form, "subject": subject})


@admin_required
def admin_booking_delete(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    subject_id = booking.subject.id
    if request.method == "POST":
        booking.delete()
        messages.success(request, "Запись удалена.")
        return redirect("admin_subject_view", subject_id=subject_id)
    return render(request, "admin/confirm_delete.html", {
        "title": "Удалить запись?",
        "object": booking,
        "cancel_url": "admin_subject_view",
        "cancel_args": [subject_id],
    })