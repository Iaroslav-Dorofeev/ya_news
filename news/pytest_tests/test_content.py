import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


def test_news_count(author_client, news_bulk):
    url = reverse('news:home')
    response = author_client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(author_client, news_bulk):
    url = reverse('news:home')
    response = author_client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(author_client, news, comment_bulk):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    news = response.context['news']
    assert 'news' in response.context
    all_timestamps = [comment.created for comment in comment_bulk]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'user_client, form_in_response',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True)
    )
)
def test_anonymous_client_has_no_form(user_client, form_in_response, news):
    url = reverse('news:detail', args=(news.id,))
    response = user_client.get(url)
    assert ('form' in response.context) is form_in_response
    if 'form' in response.context:
        assert isinstance(response.context['form'], CommentForm)
