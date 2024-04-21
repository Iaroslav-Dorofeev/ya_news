from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_anonymous_user_cant_create_comment(client, form_data, news):
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(author, author_client, form_data, news):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    # Формируем данные для отправки формы; текст включает
    # первое слово из списка стоп-слов.
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    # Отправляем запрос через авторизованный клиент.
    response = author_client.post(url, data=bad_words_data)
    # Проверяем, есть ли в ответе ошибка формы.
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    # Дополнительно убедимся, что комментарий не был создан.
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(url)
    redirect_url = (reverse('news:detail', args=(comment.news.id,))
                    + '#comments')
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment(reader_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = reader_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'user, status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
    )
)
def test_edit_comment(comment, user, status):
    url = reverse('news:edit', args=(comment.id,))
    response = user.post(url)
    assert response.status_code == status
