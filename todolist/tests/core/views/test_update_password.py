import pytest
from django.urls import reverse
from rest_framework import status

from tests.utils import BaseTestCase


@pytest.mark.django_db()
class TestUpdatePasswordView(BaseTestCase):
    url = reverse('core:password_update')

    def test_auth_required(self, client):
        """Тест на эндпоинт PATCH: /core/update_password

        Производит проверку требований аутентификации.
        """
        response = client.patch(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_invalid_old_password(self, auth_client, faker):
        """Тест на эндпоинт PATCH: /core/update_password

        Производит проверку соответствия значения поля 'old_password' значению текущего пароля.
        """
        response = auth_client.patch(self.url, data={
            'old_password': faker.password(),
            'new_password': faker.password(),
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
        assert response.json() == {'old_password': ['Old password is incorrect']}

    def test_weak_new_password(self, client, user_factory, faker, invalid_password):
        """Тест на эндпоинт POST: /core/update_password

        Производит проверку процедуры валидации нового пароля.
        Проверяется проверка пароля на соответствие следующим требованиям:
            - пароль имеет соответствующую длину
            - пароль не входит в список часто встречающихся паролей
            - пароль не состоит только из чисел
        """
        password = faker.password()
        user = user_factory.create(password=password)

        client.force_login(user)
        response = client.patch(self.url, data={
            'old_password': password,
            'new_password': invalid_password,
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_success(self, client, faker, user_factory):
        """Тест на эндпоинт PATCH: /core/update_password

        Производит проверку процедуры успешного изменения пароля.
        """
        old_password = faker.password()
        user = user_factory.create(password=old_password)

        new_password = faker.password()
        client.force_login(user)
        response = client.patch(self.url, data={
            'old_password': old_password,
            'new_password': new_password,
        })
        assert response.status_code == status.HTTP_200_OK
        assert not response.json()
        user.refresh_from_db(fields=('password',))
        assert user.check_password(new_password)
