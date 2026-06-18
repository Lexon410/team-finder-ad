import random
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from constants import (
    MAX_NAME_LENGTH, MAX_SURNAME_LENGTH, MAX_PHONE_LENGTH, MAX_ABOUT_LENGTH,
    AVATAR_SIZE, AVATAR_FONT_SIZE, AVATAR_COLORS
)
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, name, surname, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    name = models.CharField(max_length=MAX_NAME_LENGTH, verbose_name='Имя')
    surname = models.CharField(max_length=MAX_SURNAME_LENGTH, verbose_name='Фамилия')
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/default.png',
        verbose_name='Аватар'
    )
    phone = models.CharField(
        max_length=MAX_PHONE_LENGTH,
        blank=True,
        default='',
        verbose_name='Телефон'
    )
    github_url = models.URLField(blank=True, default='', verbose_name='GitHub')
    about = models.TextField(
        max_length=MAX_ABOUT_LENGTH,
        blank=True,
        default='',
        verbose_name='О себе'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.name} {self.surname}'

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            self.avatar = self.generate_avatar()
        super().save(*args, **kwargs)

    def generate_avatar(self):
        color = random.choice(AVATAR_COLORS)
        image = Image.new('RGB', (AVATAR_SIZE, AVATAR_SIZE), color)
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype('arial.ttf', AVATAR_FONT_SIZE)
        except Exception:
            font = ImageFont.load_default()
        text = self.name[0].upper()
        bbox = draw.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (AVATAR_SIZE - w) // 2
        y = (AVATAR_SIZE - h) // 2
        draw.text((x, y), text, fill='white', font=font)
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        filename = f'avatar_{self.email}.png'
        return ContentFile(buffer.getvalue(), filename)
