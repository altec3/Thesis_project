from django.db import models

from core.models import User


class BaseModel(models.Model):
    """Базовая модель

    Реализует поля с датами создания и обновления экземпляра
    """

    created = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Дата последнего обновления', auto_now=True)

    class Meta:
        abstract = True


class Board(BaseModel):
    """Модель доски"""

    title = models.CharField(verbose_name='Название', max_length=255)
    is_deleted = models.BooleanField(verbose_name='Удалена', default=False)

    class Meta:
        verbose_name = 'Доска'
        verbose_name_plural = 'Доски'

    def __str__(self):
        return self.title


class BoardParticipant(BaseModel):
    """Модель участника доски"""

    class Role(models.IntegerChoices):
        owner = 1, 'Владелец'
        writer = 2, 'Редактор'
        reader = 3, 'Читатель'

    board = models.ForeignKey(Board, verbose_name='Доска', related_name='participants', on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name='Пользователь', related_name='participants', on_delete=models.PROTECT)
    role = models.PositiveSmallIntegerField(verbose_name='Роль', choices=Role.choices, default=Role.owner)

    class Meta:
        unique_together = ('board', 'user')
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'

    def __str__(self):
        return self.board


class Category(BaseModel):
    """Модель категории"""

    title = models.CharField(verbose_name='Название', max_length=255)
    user = models.ForeignKey(User, verbose_name='Автор', related_name='categories', on_delete=models.PROTECT)
    board = models.ForeignKey(Board, verbose_name='Доска', related_name='categories', on_delete=models.PROTECT)
    is_deleted = models.BooleanField(verbose_name='Удалена', default=False)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Goal(BaseModel):
    """Модель цели"""

    class Status(models.IntegerChoices):
        to_do = 1, 'К выполнению'
        in_progress = 2, 'В процессе'
        done = 3, 'Выполнено'
        archived = 4, 'Архив'

    class Priority(models.IntegerChoices):
        low = 1, 'Низкий'
        medium = 2, 'Средний'
        high = 3, 'Высокий'
        critical = 4, 'Критический'

    user = models.ForeignKey(User, verbose_name='Автор', related_name='goals', on_delete=models.PROTECT)
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='goals', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Заголовок', max_length=255)
    description = models.TextField(verbose_name='Описание', max_length=1000, blank=True)
    status = models.PositiveSmallIntegerField(verbose_name='Статус', choices=Status.choices, default=Status.to_do)
    priority = models.PositiveSmallIntegerField(
        verbose_name='Приоритет', choices=Priority.choices, default=Priority.medium
    )
    due_date = models.DateTimeField(verbose_name='Дедлайн', null=True)

    class Meta:
        verbose_name = 'Цель'
        verbose_name_plural = 'Цели'

    def __str__(self):
        return self.title


class Comment(BaseModel):
    """Модель комментария"""

    user = models.ForeignKey(User, verbose_name='Автор', related_name='comments', on_delete=models.PROTECT)
    goal = models.ForeignKey(Goal, verbose_name='Цель', related_name='comments', on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Комментарий', max_length=1000)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        text = str(self.text)
        return text if len(text) <= 20 else text[:20] + "..."
