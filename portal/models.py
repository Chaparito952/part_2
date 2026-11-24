from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField('Название категории', max_length=100)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class RequestOrder(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новая'),
        ('in_progress', 'Принято в работу'),
        ('done', 'Выполнено'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    title = models.CharField('Название заявки', max_length=200)
    description = models.TextField('Описание заявки')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    photo = models.ImageField('Фото помещения / план', upload_to='plans/')
    design_photo = models.ImageField('Фото готового дизайна', upload_to='designs/', blank=True, null=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='new')
    comment = models.TextField('Комментарий администратора', blank=True, null=True)
    created_at = models.DateTimeField('Временная метка', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def __str__(self):
        return f'{self.title} ({self.get_status_display()})'
