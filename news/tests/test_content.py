"""Тесты для проверки содержимого страниц приложения новостей."""
import pytest
from django.urls import reverse
from django.conf import settings
from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, many_news):
    """Проверяет количество новостей на главной странице."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, many_news):
    """Проверяет сортировку новостей от новых к старым."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('reader_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_comment_form_availability(parametrized_client, news, form_in_context):
    """Проверяет доступность формы комментария для разных пользователей."""
    url = reverse('news:detail', args=(news.id,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_in_context
    if form_in_context:
        assert isinstance(response.context['form'], CommentForm)


def test_comments_order(client, news, many_comments):
    """Проверяет хронологический порядок комментариев."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    all_comments = response.context['news'].comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps
