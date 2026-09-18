# kittybot/send_random_image.py
import vk_api
import random
import requests
import io
from pprint import pprint
VK_TOKEN = 'vk1.a.rOTvy6Y8TtcUaC4SuUnaYoUVflZZ-cvEaaXUxb4AkYQ0Vv0f_ApSlKM_eSFszlOv1Evj2S9X_qkLuAxIEn-adXdCPwYSTsTZ2r7ArUFnxoxVjZzftK_VsNlRX2_U9qKScI8aoMG2S5uZj3s72X91WyBJWoXEHjSvdrSUVuDb-8O2P2kQP2zY1GsmNsz9gtvw0z58UYpTGO9iiahZDlKVRg'


vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()

screen_name = 'bukreev03'
user_info = vk.users.get(user_ids=screen_name)
user_id = user_info[0]['id']

USER_ID = user_id


# Адрес изображения
URL = 'https://aleatori.cat/random.json'

# Сделаем GET-запрос к API
response = requests.get(URL).json()
random_cat_url = response.get('url')

upload_url = vk_session.method('photos.getMessagesUploadServer', {'peer_id': USER_ID})['upload_url']

# Скачиваем картинку с найденным адресом
img_data = requests.get(random_cat_url).content

# Проверка: действительно ли это JPG файл?
if not img_data.startswith(b'\xFF\xD8\xFF'):
    print("❌ ОШИБКА: Скачанные данные НЕ являются JPG файлом!")
    print("Скорее всего, скачалась HTML-страница с ошибкой.")
    print("Первые 200 символов скачанного контента:")
    print(img_data[:200].decode('utf-8', errors='ignore')) # Пытаемся показать как текст
else:
    print("✅ Данные выглядят как валидный JPG файл.")
    print(f"Размер файла: {len(img_data)} байт")

# Отправляем файл на сервер ВК
files = {
    'photo': ('cat.jpg', io.BytesIO(img_data))
}

response = requests.post(upload_url, files=files)
result = response.json()

print("Статус код ответа:", response.status_code)
print("Полученная ссылка на картинку:", random_cat_url) 
print("Полный ответ сервера (JSON):")
pprint(result) 

# Сохраняем фото в ВК и получаем attachment
saved_photo = vk_session.method('photos.saveMessagesPhoto', {
    'photo': result['photo'],
    'server': result['server'],
    'hash': result['hash']
})[0]
owner_id = saved_photo['owner_id']
media_id = saved_photo['id']

attachment = f'photo{owner_id}_{media_id}'

# Отправляем attachment в сообщении
vk.messages.send(
    user_id=USER_ID,
    attachment=attachment,
    message=f"Вам телеграмма!",
    random_id=random.randint(0, 100000)
)
