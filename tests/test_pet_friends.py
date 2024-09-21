from api import PetFriends
from settings import valid_email, valid_password
import os
import pytest
import datetime

pf = PetFriends()


@pytest.fixture(scope="class", autouse=True)
def get_key(email=valid_email, password=valid_password):
    """Фикстура проверяет, что запрос API ключа возвращает статус 200 и в результате содержится слово key,
    и возвращает API ключ. Запускается для каждого тестового класса"""

    #  Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в pytest.key.
    status, pytest.key = pf.get_api_key(email, password)
    assert status == 200, 'Запрос выполнен неуспешно'
    assert 'key' in pytest.key, 'В запросе не передан ключ авторизации'
    return pytest.key


@pytest.fixture(scope="class", autouse=True)
def time_delta():
    """Фикстура выводит на печать время выполнения тестов. Запускается для каждого тестового класса"""
    start_time = datetime.datetime.now()
    yield
    end_time = datetime.datetime.now()
    print(f"\nТест шел: {end_time - start_time}")


def generate_string(num):
    return "x" * num


def russian_chars():
    return 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'


# 20 популярных китайских иероглифов
def chinese_chars():
    return '的一是不了人我在有他这为之大来以个中上们'


def special_chars():
    return '|\\/!@#$%^&*()-_=+`~?"№;:[]{}'


class TestPositive:
    @pytest.mark.api
    @pytest.mark.parametrize("filter", ['', 'my_pets'],
                             ids=['empty string', 'only my pets'])
    def test_get_all_pets_with_valid_key(self, get_key, filter):
        """Проверяем, что запрос на получение списка питомцев с валидными данными возвращает статус 200
        и не пустое тело ответа."""
        pytest.status, result = pf.get_list_of_pets(get_key, filter)

        # Проверяем статус ответа
        assert pytest.status == 200
        assert len(result['pets']) > 0

    @pytest.mark.api
    def test_add_new_pet_with_valid_data(self, get_key, name='Deyk', animal_type='dog', age=3,
                                         pet_photo='images/Deyk.jpg'):
        """Проверяем, что запрос на создание питомца с фото с валидными данными возвращает статус 200
        и имя созданного питомца соответствует ожидаемому."""

        # Получаем полный путь до файла с фото питомца
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        #  Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result.
        status, result = pf.add_new_pet_with_photo(get_key, name, animal_type, age, pet_photo)

        # Сверяем полученный ответ с ожидаемым результатом.
        assert status == 200
        assert result['name'] == name

    @pytest.mark.api
    def test_add_new_pet_simple_with_valid_data(self, get_key, name='Deyk', animal_type='dog', age='3'):
        """Проверяем, что запрос на создание питомца без фото с валидными данными возвращает статус 200
        и имя созданного питомца соответствует ожидаемому."""

        #  Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result.
        status, result = pf.add_new_pet_simple(get_key, name, animal_type, age)

        # Сверяем полученный ответ с ожидаемым результатом.
        assert status == 200
        assert result['name'] == name

    @pytest.mark.api
    @pytest.mark.parametrize("name", [generate_string(255), generate_string(1001),
                                      russian_chars(), russian_chars().upper(),
                                      chinese_chars(), special_chars(), '123'],
                             ids=['255 symbols', 'more than 1000 symbols',
                                  'russian', 'RUSSIAN',
                                  'chinese', 'specials', 'digit'])
    @pytest.mark.parametrize("animal_type", [generate_string(255), generate_string(1001),
                                             russian_chars(), russian_chars().upper(),
                                             chinese_chars(), special_chars(), '123'],
                             ids=['255 symbols', 'more than 1000 symbols',
                                  'russian', 'RUSSIAN',
                                  'chinese', 'specials', 'digit'])
    @pytest.mark.parametrize("age", ['1'], ids=['min'])
    def test_add_new_pet_simple_with_different_valid_data(self, get_key, name, animal_type, age):
        """Проверяем, что запрос на создание питомца без фото с различными валидными данными возвращает статус 200
        и данные питомца соответствуют ожидаемым."""

        # Добавляем питомца
        pytest.status, result = pf.add_new_pet_simple(get_key, name, animal_type, age)

        # Сверяем полученный ответ с ожидаемым результатом
        assert pytest.status == 200
        assert result['name'] == name
        assert result['age'] == age
        assert result['animal_type'] == animal_type

    @pytest.mark.api
    def test_update_pet_info_with_valid_data(self, get_key, name='Deyk', animal_type='dog', age=5):
        """Проверяем, что запрос на обновление данных о своем последнем созданном питомце
        с валидными данными возвращает статус 200 и обновленные данные соответствуют ожидаемым."""

        # Получаем список своих питомцев.
        _, my_pets = pf.get_list_of_pets(get_key, 'my_pets')

        # Если список не пустой, обновляем данные о своем последнем созданном питомце.
        if len(my_pets['pets']) > 0:
            #  Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result.
            status, result = pf.update_pet_info(get_key, my_pets['pets'][0]['id'], name, animal_type, age)

            # Сверяем полученный ответ с ожидаемым результатом.
            assert status == 200
            assert result['name'] == name
            assert result['animal_type'] == animal_type
            assert result['age'] == str(age)

        # Если список пустой, вызываем исключение с сообщением об отсутствии своих питомцев.
        else:
            raise Exception("There aren't my pets.")

    @pytest.mark.api
    def test_delete_pet_with_valid_data(self, get_key):
        """Проверяем, что запрос на удаление питомца с валидными данными возвращает статус 200
        и id удаленного питомца нет в списке питомцев."""

        # Получаем список своих питомцев.
        _, my_pets = pf.get_list_of_pets(get_key, 'my_pets')

        # Если список не пустой, удаляем питомца, созданного последним.
        if len(my_pets['pets']) > 0:
            # Берем id питомца, созданного последним.
            pet_id = my_pets['pets'][0]['id']

            # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status.
            status = pf.delete_pet(get_key, pet_id)

            # Повторно запрашиваем список своих питомцев.
            _, my_pets = pf.get_list_of_pets(get_key, 'my_pets')

            # Сверяем полученный ответ с ожидаемым результатом.
            assert status == 200
            assert pet_id not in my_pets

        # Если список пустой, вызываем исключение с сообщением об отсутствии своих питомцев.
        else:
            raise Exception("There aren't my pets.")

    @pytest.mark.api
    def test_add_pet_photo_with_valid_data(self, get_key, pet_photo='images/Deyk.jpg'):
        """Проверяем, что запрос на добавление фото питомца с валидными данными возвращает статус 200
        и id созданного питомца соответствует ожидаемому."""

        # Получаем полный путь до файла с фото питомца
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        # Получаем список своих питомцев.
        _, my_pets = pf.get_list_of_pets(get_key, 'my_pets')

        # Если список не пустой, добавляем фото для своего последнего созданного питомца.
        if len(my_pets['pets']) > 0:
            #  Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result.
            status, result = pf.add_pet_photo(get_key, my_pets['pets'][0]['id'], pet_photo)

            # Сверяем полученный ответ с ожидаемым результатом.
            assert status == 200
            assert result['id'] == my_pets['pets'][0]['id']

        # Если список пустой, вызываем исключение с сообщением об отсутствии своих питомцев.
        else:
            raise Exception("There aren't my pets.")


class TestNegative:
    @pytest.mark.auth
    def test_unsuccessful_get_api_key_with_empty_email(self, email='', password=valid_password):
        """Проверяем, что запрос API ключа с пустым значением email возвращает статус 403."""

        # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status.
        status, _ = pf.get_api_key(email, password)

        # Сверяем полученный ответ с ожидаемым результатом.
        assert status == 403

    @pytest.mark.auth
    def test_unsuccessful_get_api_key_with_empty_password(self, email=valid_email, password=''):
        """Проверяем, что запрос API ключа с пустым значением пароля возвращает статус 403."""

        # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status.
        status, _ = pf.get_api_key(email, password)

        # Сверяем полученный ответ с ожидаемым результатом.
        assert status == 403

    @pytest.mark.auth
    def test_unsuccessful_get_api_key_with_empty_params(self, email='', password=''):
        """Проверяем, что запрос API ключа с пустыми полями возвращает статус 403."""

        # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status.
        status, _ = pf.get_api_key(email, password)

        # Сверяем полученный ответ с ожидаемым результатом.
        assert status == 403

    @pytest.mark.auth
    def test_unsuccessful_get_api_key_with_swap_params(self, email=valid_email, password=valid_password):
        """Проверяем, что запрос API ключа с валидным email в поле пароля
        и валидным паролем в поле email возвращает статус 403."""

        # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status.
        status, _ = pf.get_api_key(password, email)

        # Сверяем полученный ответ с ожидаемым результатом.
        assert status == 403

    @pytest.mark.auth
    def test_unsuccessful_get_api_key_with_invalid_password(self, email=valid_email, password=valid_password + 'a'):
        """Проверяем, что запрос API ключа с невалидным паролем возвращает статус 403."""

        # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status.
        status, _ = pf.get_api_key(email, password)

        # Сверяем полученный ответ с ожидаемым результатом.
        assert status == 403

    @pytest.mark.api
    @pytest.mark.parametrize("filter", [generate_string(255), generate_string(1001),
                                        russian_chars(), russian_chars().upper(),
                                        chinese_chars(), special_chars(), 123],
                             ids=['255 symbols', 'more than 1000 symbols',
                                  'russian', 'RUSSIAN',
                                  'chinese', 'specials', 'digit'])
    @pytest.mark.skip(reason="API запрос GET_/api/pets работает с ошибкой.")
    def test_unsuccessful_get_all_pets_with_invalid_filter(self, get_key, filter):
        """Проверяем, что запрос на получение списка питомцев с невалидными значениями параметра "filter" возвращает
         статус 400.
        API запрос работает с ошибкой. Вместо кода 400 приходит код 500."""
        pytest.status, result = pf.get_list_of_pets(get_key, filter)

        # Проверяем статус ответа
        assert pytest.status == 400

    @pytest.mark.api
    @pytest.mark.skip(reason="API запрос POST_/api/pets работает с ошибкой.")
    def test_unsuccessful_add_new_pet_with_gif_file(self, get_key, name='Deyk', animal_type='dog', age=3,
                                                    pet_photo='images/Deyk.gif'):
        """Проверяем, что запрос на создание питомца с файлом gif вместо фото возвращает статус 400.
        API запрос работает с ошибкой. При создании питомца с файлом gif создается питомец без фото.
        Вместо кода 400 приходит код 200."""

        # Получаем полный путь до файла с фото питомца
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        #  Отправляем запрос и сохраняем полученный ответ с кодом статуса в status.
        status, _ = pf.add_new_pet_with_photo(get_key, name, animal_type, age, pet_photo)

        # Сверяем полученный ответ с ожидаемым результатом.
        assert status == 400

    @pytest.mark.api
    @pytest.mark.xfail(reason="API запрос POST_/api/create_pet_simple работает с ошибкой.")
    def test_unsuccessful_add_new_pet_simple_with_str_age(self, get_key, name='Deyk', animal_type='dog',
                                                                 age='five'):
        """Проверяем, что запрос на создание питомца без фото со строковым значением возраста возвращает статус 400.
        API запрос работает с ошибкой. Питомец создается со строковым значением возраста.
        Вместо кода 400 приходит код 200."""

        #  Отправляем запрос и сохраняем полученный ответ с кодом статуса в status.
        status, _ = pf.add_new_pet_simple(get_key, name, animal_type, age)

        # Сверяем полученный ответ с ожидаемым результатом.
        assert status == 400

    @pytest.mark.api
    @pytest.mark.skip(reason="API запрос POST_/api/create_pet_simple работает с ошибкой.")
    @pytest.mark.parametrize("name", [''], ids=['empty'])
    @pytest.mark.parametrize("animal_type", [''], ids=['empty'])
    @pytest.mark.parametrize("age", ['', '-1', '0', '100', '1.5',
                                     '2147483647', '2147483648', special_chars(),
                                     russian_chars(), russian_chars().upper(), chinese_chars()],
                             ids=['empty', 'negative', 'zero', 'greater than max', 'float',
                                  'int_max', 'int_max + 1', 'specials',
                                  'russian', 'RUSSIAN', 'chinese'])
    def test_unsuccessful_add_new_pet_simple_with_invalid_params(self, name, animal_type, age):
        """Проверяем, что запрос на создание питомца без фото с невалидными значениями параметров возвращает статус 400.
        API запрос работает с ошибкой. Вместо кода 400 приходит код 200."""

        # Добавляем питомца
        pytest.status, result = pf.add_new_pet_simple(get_key, name, animal_type, age)

        # Сверяем полученный ответ с ожидаемым результатом
        assert pytest.status == 400

    @pytest.mark.api
    @pytest.mark.skip(reason="API запрос POST_/api/pets работает с ошибкой.")
    def test_unsuccessful_add_new_pet_simple_with_empty_name(self, get_key, name='', animal_type='dog', age=5):
        """Проверяем, что запрос на создание питомца без фото с пустым значением имени возвращает статус 400.
        API запрос работает с ошибкой. Питомец создается без имени.
        Вместо кода 400 приходит код 200."""

        #  Отправляем запрос и сохраняем полученный ответ с кодом статуса в status.
        status, _ = pf.add_new_pet_simple(get_key, name, animal_type, age)

        # Сверяем полученный ответ с ожидаемым результатом.
        assert status == 400
