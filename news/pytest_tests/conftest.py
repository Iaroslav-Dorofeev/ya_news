from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Лев Толстой')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель простой')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news(author):
    news = News.objects.create(
        title='Заголовок',
        text='Текст простой'
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def news_id(comment):
    return (comment.news.id, )


@pytest.fixture
def news_bulk(author):
    today = datetime.today()
    news_bulk = News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        ) for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return news_bulk


@pytest.fixture
def comment_bulk(news, author):
    now = timezone.now()
    # Создаём комментарии в цикле.
    for index in range(10):
        # Создаём объект и записываем его в переменную.
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=index)
        # И сохраняем эти изменения.
        comment.save()
    comments = news.comment_set.all()
    return comments


@pytest.fixture
def form_data():
    return {'text': 'Текст комментария'}
