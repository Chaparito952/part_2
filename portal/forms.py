import re
import os
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import RequestOrder, Category


class UserRegistrationForm(forms.Form):
    full_name = forms.CharField(label='ФИО', max_length=150)
    username = forms.CharField(label='Логин', max_length=150)
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput)
    agree = forms.BooleanField(
        label='Согласие на обработку персональных данных',
        required=True,
        error_messages={'required': 'Необходимо дать согласие на обработку персональных данных.'}
    )

    def clean_full_name(self):
        full_name = self.cleaned_data['full_name']
        if not re.match(r'^[А-Яа-яЁё\s-]+$', full_name):
            raise ValidationError('ФИО должно содержать только кириллические буквы, дефис и пробелы.')
        return full_name

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[A-Za-z-]+$', username):
            raise ValidationError('Логин должен содержать только латиницу и дефис.')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким логином уже существует.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Введенные пароли не совпадают.')
        return cleaned_data

class RequestOrderForm(forms.ModelForm):
    class Meta:
        model = RequestOrder
        fields = ['title', 'description', 'category', 'photo']
        labels = {
            'title': 'Название заявки',
            'description': 'Описание',
            'category': 'Категория',
            'photo': 'Фото помещения или его план (jpg, jpeg, png, bmp, до 2 МБ)',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if not photo:
            raise ValidationError('Необходимо прикрепить фото помещения или его план.')

        # 1. Проверка расширения файла
        ext = os.path.splitext(photo.name)[1].lower()
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        if ext not in allowed_extensions:
            raise ValidationError('Недопустимый формат файла. Разрешены только: jpg, jpeg, png, bmp.')

        # 2. Проверка размера файла (максимум 2 МБ = 2 * 1024 * 1024 байт)
        max_size = 2 * 1024 * 1024
        if photo.size > max_size:
            raise ValidationError('Размер файла превышает 2 МБ.')

        return photo

class CompleteOrderForm(forms.ModelForm):
    class Meta:
        model = RequestOrder
        fields = ['design_photo']
        labels = {
            'design_photo': 'Изображение созданного дизайна (jpg, jpeg, png, bmp, до 2 МБ)',
        }
        widgets = {
            'design_photo': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_design_photo(self):
        photo = self.cleaned_data.get('design_photo')
        if not photo:
            raise ValidationError('Для перевода в статус «Выполнено» необходимо прикрепить изображение дизайна.')

        ext = os.path.splitext(photo.name)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.bmp']:
            raise ValidationError('Недопустимый формат файла. Разрешены только: jpg, jpeg, png, bmp.')

        if photo.size > 2 * 1024 * 1024:
            raise ValidationError('Размер файла превышает 2 МБ.')

        return photo


class InProgressOrderForm(forms.ModelForm):
    class Meta:
        model = RequestOrder
        fields = ['comment']
        labels = {
            'comment': 'Комментарий администратора (обязательно)',
        }
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_comment(self):
        comment = self.cleaned_data.get('comment', '').strip()
        if not comment:
            raise ValidationError('Укажите комментарий при переводе заявки в статус «Принято в работу».')
        return comment


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        labels = {
            'name': 'Название новой категории',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: 3D-дизайн'}),
        }