# kittybot/kittybot.py
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import vk_api
import random
import requests
import io

from pprint import pprint

VK_TOKEN = 'vk1.a.0LdpztSkvHA2RtON0R79rVl5wVRTQbVgC_gqDnirRfNQTeasX7osxonm6nJIV2bs84b7Z-vSjMMiTHfJ_RLU-6HsaPc7MP1FrO0nUzQL9XM95f_QgBzktLR6CSTPKTGuD-7rnUOYfkKeaRwq9RXXTMtQFXk2xIoxDw1zdWAkKyPn95gEH_KdKm36TbugXaoAUy6qyPg0QKqt2t4qFmCzrw'
GROUP_ID = 241517733

# Авторизация
vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)


def get_user_name(vk, user_id):
    user_info = vk.users.get(user_ids=user_id)[0]
    return user_info['first_name']


# Функция для получения случайного URL от API
def get_new_image():
    url = 'https://api.thecatapi.com/v1/images/search'
    response = requests.get(url).json()
    return response[0]['url']


# Функция для загрузки картинки на сервер и формирования attachment
def upload_image(vk_session, peer_id, image_url):
    # Получаем адрес для загрузки
    upload_url = vk_session.method('photos.getMessagesUploadServer', {'peer_id': peer_id})['upload_url']

    # Скачиваем картинку
    img_data = requests.get(image_url).content

    # Отправляем файл на сервер ВК
    files = {'photo': ('cat.jpg', io.BytesIO(img_data))}
    response = requests.post(upload_url, files=files)
    result = response.json()

    # Сохраняем фото в ВК и получаем attachment
    saved_photo = vk_session.method('photos.saveMessagesPhoto', {
        'photo': result['photo'],
        'server': result['server'],
        'hash': result['hash']
    })[0]
    owner_id = saved_photo['owner_id']
    media_id = saved_photo['id']
    return f'photo{owner_id}_{media_id}'


def handle_start(vk, vk_session, message):
    user_id = message['from_id']
    peer_id = message['peer_id']
    name = get_user_name(vk, user_id)

    # Получаем URL случайной картинки
    image_url = get_new_image()
    # Формируем вложение
    attachment = upload_image(vk_session, peer_id, image_url)
    # Отправляем сообщение
    vk.messages.send(
        user_id=user_id,
        attachment=attachment,
        message=f"Привет, {name}. Посмотри, какого котика я тебе нашёл",
        random_id=random.randint(0, 100000)
    )

def handle_cat(vk, vk_session, message):
    user_id = message['from_id']
    peer_id = message['peer_id']

    # Получаем URL случайной картинки
    image_url = get_new_image()
    # Формируем вложение
    attachment = upload_image(vk_session, peer_id, image_url)
    # Отправляем сообщение
    vk.messages.send(
        user_id=user_id,
        attachment=attachment,
        random_id=random.randint(0, 100000)
    )

def handle_text(vk, message):
    user_id = message['from_id']
    vk.messages.send(
        user_id=user_id,
        message="Привет, я KittyBot!",
        random_id=random.randint(0, 100000)
    )

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        message = event.object.message
        text = message.get('text', '').strip().lower()
        if text:
            if text == 'начать':
                handle_start(vk, vk_session, message)
            elif text == 'хочу котика':
                handle_cat(vk, vk_session, message)
            else:
                handle_text(vk, message) 