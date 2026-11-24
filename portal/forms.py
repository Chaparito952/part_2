import re
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
