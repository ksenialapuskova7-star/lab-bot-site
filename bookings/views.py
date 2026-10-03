from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import RegisterForm, LoginForm
from .models import Student, Subject, Booking


# ============ ГЛАВНАЯ ============

def index(request):
    if request.user.is_authenticated:
        return redirect("subjects")
    return render(request, "index.html")


# ============ РЕГИСТРАЦИЯ ============

def register(request):
    if request.user.is_authenticated:
        return redirect("subjects")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            student_id = form.cleaned_data["student_id"]
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]

            try:
                with transaction.atomic():
                    student = Student.objects.select_for_update().get(id=student_id)
                    if student.is_registered:
                        messages.error(request, "Этот студент уже зарегистрирован.")
                        return render(request, "register.html", {"form": form})

                    user = User.objects.create_user(username=username, password=password)
                    student.user = user
                    student.is_registered = True
                    student.save()

                login(request, user)
                messages.success(request, f"Добро пожаловать, {student.full_name}!")
                return redirect("subjects")
            except IntegrityError:
                messages.error(request, "Ошибка регистрации. Попробуйте ещё раз.")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


# ============ ВХОД / ВЫХОД ============

def login_view(request):
    if request.user.is_authenticated:
        return redirect("subjects")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                return redirect("subjects")
            messages.error(request, "Неверный логин или пароль.")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("index")


# ============ ПРЕДМЕТЫ ============

def subjects(request):
    if not request.user.is_authenticated:
        return redirect("login")

    # Показываем только активные будущие предметы
    from django.utils import timezone

    now = timezone.now()
    all_subjects = Subject.objects.filter(is_active=True, date__gte=now.date())
    available = [s for s in all_subjects if s.is_open]
    upcoming = [s for s in all_subjects if not s.is_open and s.start_datetime > now]

    return render(
        request,
        "subjects.html",
        {"available": available, "upcoming": upcoming},
    )


def subject_detail(request, subject_id):
    if not request.user.is_authenticated:
        return redirect("login")

    subject = get_object_or_404(Subject, id=subject_id, is_active=True)

    if not subject.is_open:
        messages.error(request, "Запись на этот предмет ещё не открыта или уже закрыта.")
        return redirect("subjects")

    student = request.user.student

    # Уже записан?
    already = Booking.objects.filter(subject=subject, student=student).first()

    booked_slots = set(subject.bookings.values_list("slot_number", flat=True))
    slots = [
        {"number": i, "is_booked": i in booked_slots}
        for i in range(1, subject.max_slots + 1)
    ]

    return render(
        request,
        "subject.html",
        {
            "subject": subject,
            "slots": slots,
            "already_booked": already,
            "bookings": subject.bookings.select_related("student").order_by("slot_number"),
        },
    )


@require_POST
def book_slot(request, subject_id):
    if not request.user.is_authenticated:
        return redirect("login")

    subject = get_object_or_404(Subject, id=subject_id, is_active=True)

    if not subject.is_open:
        messages.error(request, "Запись закрыта.")
        return redirect("subjects")

    slot_number = int(request.POST.get("slot_number", 0))
    if slot_number < 1 or slot_number > subject.max_slots:
        messages.error(request, "Неверное место.")
        return redirect("subject_detail", subject_id=subject.id)

    student = request.user.student

    try:
        with transaction.atomic():
            Booking.objects.create(
                subject=subject,
                slot_number=slot_number,
                student=student,
                last_name=student.last_name,
            )
        messages.success(request, f"Вы записаны на место {slot_number}!")
    except IntegrityError:
        messages.error(request, "Это место уже занято или вы уже записаны.")

    return redirect("subject_detail", subject_id=subject.id)


# ============ МОИ ЗАПИСИ ============

def my_bookings(request):
    if not request.user.is_authenticated:
        return redirect("login")

    student = request.user.student
    bookings = (
        Booking.objects.filter(student=student)
        .select_related("subject")
        .order_by("subject__date", "subject__start_time")
    )
    return render(request, "my_bookings.html", {"bookings": bookings})


@require_POST
def cancel_booking(request, booking_id):
    if not request.user.is_authenticated:
        return redirect("login")

    student = request.user.student
    booking = get_object_or_404(Booking, id=booking_id, student=student)
    booking.delete()
    messages.success(request, "Запись отменена.")
    return redirect("my_bookings")