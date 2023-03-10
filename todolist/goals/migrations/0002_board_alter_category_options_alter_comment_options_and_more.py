# Generated by Django 4.1.4 on 2023-01-23 04:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('goals', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Дата последнего обновления')),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='Удалена')),
            ],
            options={
                'verbose_name': 'Доска',
                'verbose_name_plural': 'Доски',
            },
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'default_related_name': 'categories', 'verbose_name': 'Категория', 'verbose_name_plural': 'Категории'},
        ),
        migrations.AlterModelOptions(
            name='comment',
            options={'default_related_name': 'comments', 'verbose_name': 'Комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
        migrations.AlterModelOptions(
            name='goal',
            options={'default_related_name': 'goals', 'verbose_name': 'Цель', 'verbose_name_plural': 'Цели'},
        ),
        migrations.AlterField(
            model_name='category',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='goal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='goals.goal', verbose_name='Цель'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='goal',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='goals.category', verbose_name='Категория'),
        ),
        migrations.AlterField(
            model_name='goal',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AddField(
            model_name='category',
            name='board',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='goals.board', verbose_name='Доска'),
        ),
        migrations.CreateModel(
            name='BoardParticipant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Дата последнего обновления')),
                ('role', models.PositiveSmallIntegerField(choices=[(1, 'Владелец'), (2, 'Редактор'), (3, 'Читатель')], default=1, verbose_name='Роль')),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='goals.board', verbose_name='Доска')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Участник',
                'verbose_name_plural': 'Участники',
                'default_related_name': 'participants',
                'unique_together': {('board', 'user')},
            },
        ),
    ]
