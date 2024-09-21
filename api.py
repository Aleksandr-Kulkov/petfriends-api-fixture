import requests
import json
from requests_toolbelt import MultipartEncoder


class PetFriends:
    def __init__(self):
        self.base_url = "https://petfriends.skillfactory.ru/"

    def get_api_key(self, email: str, password: str) -> json:
        """Метод делает запрос к API сервера и возвращает статус запроса и результат в формате
        JSON с уникальным ключом пользователя, найденного по указанным email и паролем."""

        headers = {
            'email': email,
            'password': password
        }

        res = requests.get(self.base_url+'api/key', headers=headers)

        status = res.status_code
        result = ""
        try:
            result = res.json()
        except:
            result = res.text
        return status, result

    def get_list_of_pets(self, get_key: json, filter: str = "") -> json:
        """Метод делает запрос к API сервера и возвращает статус запроса и результат в формате
        JSON со списком найденных питомцев, совпадающих с фильтром. Фильтр может иметь
        либо пустое значение - получить список всех питомцев, либо 'my_pets' - получить
        список питомцев пользователя."""

        headers = {'auth_key': get_key['key']}
        filter = {'filter': filter}

        res = requests.get(self.base_url+'api/pets', headers=headers, params=filter)

        status = res.status_code
        result = ""
        try:
            result = res.json()
        except:
            result = res.text
        return status, result

    def add_new_pet_with_photo(self, get_key: json, name: str, animal_type: str, age: int, pet_photo: str) -> json:
        """Метод делает запрос к API сервера и возвращает статус запроса и результат в формате
        JSON с данными созданного питомца."""

        headers = {'auth_key': get_key['key']}
        data = {
            'name': name,
            'animal_type': animal_type,
            'age': age
        }
        file = {'pet_photo': (pet_photo, open(pet_photo, 'rb'), 'image/jpeg')}

        res = requests.post(self.base_url + 'api/pets', headers=headers, data=data, files=file)

        status = res.status_code
        result = ""
        try:
            result = res.json()
        except:
            result = res.text
        return status, result

    def update_pet_info(self, get_key: json, pet_id: str, name: str, animal_type: str, age: int) -> json:
        """Метод делает запрос к API сервера и возвращает статус запроса и результат в формате
        JSON с обновленными данными питомца с указанным id."""

        headers = {'auth_key': get_key['key']}
        data = {
            'name': name,
            'animal_type': animal_type,
            'age': age
        }

        res = requests.put(self.base_url + 'api/pets/' + pet_id, headers=headers, data=data)

        status = res.status_code
        result = ""
        try:
            result = res.json()
        except:
            result = res.text
        return status, result

    def delete_pet(self, get_key: json, pet_id: str) -> int:
        """Метод делает запрос к API сервера на удаление питомца и возвращает статус запроса."""

        headers = {'auth_key': get_key['key']}

        res = requests.delete(self.base_url + 'api/pets/' + pet_id, headers=headers)

        status = res.status_code
        return status

    def add_new_pet_simple(self, auth_key: json, name: str, animal_type: str, age: int) -> json:
        """Метод отправляет на сервер данные о добавляемом питомце и возвращает статус
        запроса и результат в формате JSON с данными добавленного питомца."""

        data = MultipartEncoder(
            fields={
                'name': name,
                'animal_type': animal_type,
                'age': age
            })
        headers = {'auth_key': auth_key['key'], 'Content-Type': data.content_type}

        res = requests.post(self.base_url + 'api/create_pet_simple', headers=headers, data=data)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        print(result)
        return status, result

    def add_pet_photo(self, get_key: json, pet_id: str, pet_photo: str) -> json:
        """Метод делает запрос к API сервера и возвращает статус запроса и результат в формате
        JSON с данными питомца, для которого добавлено фото."""

        headers = {'auth_key': get_key['key']}
        file = {'pet_photo': (pet_photo, open(pet_photo, 'rb'), 'image/jpeg')}

        res = requests.post(self.base_url + 'api/pets/set_photo/' + pet_id, headers=headers, files=file)

        status = res.status_code
        result = ""
        try:
            result = res.json()
        except:
            result = res.text
        return status, result
