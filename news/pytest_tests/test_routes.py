from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
def test_pages_availability(client, name, args, comment):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
@pytest.mark.parametrize(
    'user, status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
    )
)
def test_availability_for_comment_edit_and_delete(name, user, status, comment):
    url = reverse(name, args=(comment.id,))
    response = user.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_redirect_for_anonymous_client(name, comment, client):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
