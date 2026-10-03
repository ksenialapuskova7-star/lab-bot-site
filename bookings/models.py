from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Student(models.Model):
    """Профиль студента, связанный с Django User"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student",
        null=True,
        blank=True,
    )  
    last_name = models.CharField("Фамилия", max_length=100)
    first_name = models.CharField("Имя", max_length=100)
    group_name = models.CharField("Группа", max_length=50)
    is_registered = models.BooleanField("Зарегистрирован", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"
        ordering = ["group_name", "last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.group_name})"

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"


class Subject(models.Model):
    """Предмет (лаба/экзамен)"""

    TYPE_CHOICES = [
        ("lab", "Лабораторная работа"),
        ("exam", "Экзамен"),
    ]

    name = models.CharField("Название", max_length=200)
    type = models.CharField("Тип", max_length=10, choices=TYPE_CHOICES, default="lab")
    date = models.DateField("Дата")
    start_time = models.TimeField("Время начала")
    end_time = models.TimeField("Время окончания")
    max_slots = models.PositiveIntegerField("Максимум мест", default=10)
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.name} ({self.date} {self.start_time})"

    @property
    def start_datetime(self):
        """Дата и время начала"""
        naive = datetime.combine(self.date, self.start_time)
        return timezone.make_aware(naive, timezone.get_current_timezone())

    @property
    def is_open(self):
        """Запись открыта: за HOURS_BEFORE_OPEN часов до начала и до самого начала"""
        now = timezone.now()
        open_time = self.start_datetime - timedelta(hours=settings.HOURS_BEFORE_OPEN)
        return open_time <= now < self.start_datetime

    @property
    def booked_count(self):
        return self.bookings.count()

    @property
    def free_slots(self):
        return max(0, self.max_slots - self.booked_count)

    @property
    def type_display(self):
        return "Лабораторная" if self.type == "lab" else "Экзамен"


class Booking(models.Model):
    """Запись студента на предмет"""

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="bookings")
    slot_number = models.PositiveIntegerField("Место")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="bookings")
    last_name = models.CharField("Фамилия (снимок)", max_length=100)
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        unique_together = [("subject", "slot_number"), ("subject", "student")]
        ordering = ["subject", "slot_number"]

    def __str__(self):
        return f"{self.subject.name} — место {self.slot_number} — {self.last_name}"