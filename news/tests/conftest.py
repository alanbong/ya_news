"""Фикстуры для тестирования приложения news."""

import pytest
from django.test.client import Client
from news.models import Comment, News
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

@pytest.fixture
def author(django_user_model):
    """Фикстура для создания автора."""
    return django_user_model.objects.create(username='Лев Толстой')


@pytest.fixture
def reader(django_user_model):
    """Фикстура для создания читателя."""
    return django_user_model.objects.create(username='Читатель простой')


@pytest.fixture
def news():
    """Фикстура для создания новости."""
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def comment(news, author):
    """Фикстура для создания комментария."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def author_client(author):
    """Фикстура для создания клиента с авторизацией автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    """Фикстура для создания клиента с авторизацией читателя."""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def many_news():
    """Фикстура для создания нескольких новостей."""
    today = timezone.now()
    news_list = [
        News.objects.create(
            title=f'Новость {i}',
            text='Просто текст.',
            date=today - timedelta(days=i)
        ) for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return news_list


@pytest.fixture
def many_comments(news, author):
    """Фикстура для создания нескольких комментариев."""
    now = timezone.now()
    comments = []
    for i in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {i}'
        )
        comment.created = now + timedelta(days=i)
        comment.save()
        comments.append(comment)
    return comments


@pytest.fixture
def form_data():
    """Фикстура с данными формы комментария."""
    return {'text': 'Текст комментария'}
