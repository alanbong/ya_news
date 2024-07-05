"""Тесты для проверки логики работы с комментариями в приложении новостей."""

import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse
from http import HTTPStatus

from news.models import Comment
from news.forms import BAD_WORDS, WARNING

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, news, form_data):
    """Анонимный пользователь не может создать комментарий."""
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, news, author, form_data):
    """Авторизованный пользователь может создать комментарий."""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news):
    """Пользователь не может использовать запрещенные слов в комментарии."""
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.FOUND),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
    ),
)
def test_comment_delete_availability(
    parametrized_client, comment, expected_status
):
    """Доступность удаления комментария для разных пользователей."""
    url = reverse('news:delete', args=(comment.id,))
    response = parametrized_client.delete(url)
    assert response.status_code == expected_status


def test_author_can_delete_comment(author_client, comment):
    """Автор может удалить свой комментарий."""
    url = reverse('news:delete', args=(comment.id,))
    redirect_url = reverse(
        'news:detail', args=(comment.news.id,)
    ) + '#comments'
    response = author_client.delete(url)
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.FOUND),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
    ),
)
def test_comment_edit_availability(
    parametrized_client, comment, form_data, expected_status
):
    """Доступность редактирования комментария для разных пользователей."""
    url = reverse('news:edit', args=(comment.id,))
    response = parametrized_client.post(url, data=form_data)
    assert response.status_code == expected_status


def test_author_can_edit_comment(author_client, comment, form_data):
    """Автор может отредактировать свой комментарий."""
    url = reverse('news:edit', args=(comment.id,))
    redirect_url = reverse(
        'news:detail', args=(comment.news.id,)
    ) + '#comments'
    response = author_client.post(url, data=form_data)
    assertRedirects(response, redirect_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']
