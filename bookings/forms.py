from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import Student, Subject


class RegisterForm(forms.Form):
    """Форма первичной регистрации студента (выбор себя из списка + пароль)"""

    group_name = forms.ChoiceField(
        label="Группа",
        widget=forms.Select(attrs={"class": "form-control", "id": "id_group"}),
    )
    student_id = forms.ChoiceField(
        label="Фамилия и имя",
        widget=forms.Select(attrs={"class": "form-control", "id": "id_student"}),
    )
    username = forms.CharField(
        label="Логин",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Например: ivanov"}),
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    password2 = forms.CharField(
        label="Повтор пароля",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Группы — уникальные значения из незарегистрированных студентов
        groups = (
            Student.objects.filter(is_registered=False)
            .values_list("group_name", flat=True)
            .distinct()
            .order_by("group_name")
        )
        self.fields["group_name"].choices = [("", "— выберите группу —")] + [
            (g, g) for g in groups
        ]

        # Студенты — все незарегистрированные
        students = Student.objects.filter(is_registered=False).order_by(
            "group_name", "last_name", "first_name"
        )
        self.fields["student_id"].choices = [("", "— выберите себя —")] + [
            (str(s.id), f"{s.last_name} {s.first_name} ({s.group_name})")
            for s in students
        ]

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Такой логин уже занят.")
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Пароли не совпадают.")
        if p1:
            try:
                validate_password(p1)
            except forms.ValidationError as e:
                self.add_error("password1", e)
        return cleaned


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(attrs={"class": "form-control", "autofocus": True}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )


class AdminLoginForm(forms.Form):
    password = forms.CharField(
        label="Пароль администратора",
        widget=forms.PasswordInput(attrs={"class": "form-control", "autofocus": True}),
    )


class StudentAddForm(forms.ModelForm):
    """Админ добавляет студента в белый список"""

    class Meta:
        model = Student
        fields = ["last_name", "first_name", "group_name"]
        widgets = {
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "group_name": forms.TextInput(attrs={"class": "form-control"}),
        }


class SubjectForm(forms.ModelForm):
    """Админ создаёт предмет"""

    class Meta:
        model = Subject
        fields = ["name", "type", "date", "start_time", "end_time", "max_slots"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "type": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "start_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "max_slots": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 50}),
        }


class ForceBookForm(forms.Form):
    """Принудительная запись студента админом"""

    student_id = forms.ChoiceField(
        label="Студент",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    slot_number = forms.ChoiceField(
        label="Место",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, subject=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.subject = subject

        if subject:
            booked_slots = set(subject.bookings.values_list("slot_number", flat=True))
            free = [(i, f"Место {i}") for i in range(1, subject.max_slots + 1) if i not in booked_slots]
            self.fields["slot_number"].choices = free or [("", "Нет свободных мест")]

        students = Student.objects.filter(is_registered=True).order_by(
            "group_name", "last_name", "first_name"
        )
        self.fields["student_id"].choices = [
            (str(s.id), f"{s.last_name} {s.first_name} ({s.group_name})") for s in students
        ]