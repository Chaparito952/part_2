import re
import os
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


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