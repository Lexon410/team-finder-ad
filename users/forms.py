import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import User


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = re.sub(r'\D', '', phone)
            if phone.startswith('8'):
                phone = '+7' + phone[1:]
            elif phone.startswith('7'):
                phone = '+' + phone
            elif not phone.startswith('+'):
                phone = '+' + phone
            if not re.match(r'^\+7\d{10}$', phone):
                raise ValidationError('Номер должен быть в формате +7XXXXXXXXXX')
            if User.objects.exclude(pk=self.instance.pk).filter(phone=phone).exists():
                raise ValidationError('Этот номер уже используется')
        return phone

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url and 'github.com' not in url:
            raise ValidationError('Ссылка должна вести на GitHub')
        return url
