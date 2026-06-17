from django.db import models
from django.conf import settings
from constants import (
    MAX_PROJECT_NAME_LENGTH,
    MAX_STATUS_LENGTH,
    MAX_SKILL_NAME_LENGTH,
    STATUS_CHOICES,
    STATUS_OPEN,
)

class Skill(models.Model):
    name = models.CharField(max_length=MAX_SKILL_NAME_LENGTH, unique=True, verbose_name='Название')

    class Meta:
        ordering = ['name']
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=MAX_PROJECT_NAME_LENGTH, verbose_name='Название проекта')
    description = models.TextField(blank=True, verbose_name='Описание')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    github_url = models.URLField(blank=True, verbose_name='Ссылка на GitHub')
    status = models.CharField(
        max_length=MAX_STATUS_LENGTH,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
        verbose_name='Статус'
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='participated_projects',
        blank=True,
        verbose_name='Участники'
    )
    skills = models.ManyToManyField(
        Skill,
        related_name='projects',
        blank=True,
        verbose_name='Необходимые навыки'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.name