# kittybot/kittybot.py
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from dotenv import load_dotenv
import io
import json
import logging
import os
import random
import requests
import vk_api


load_dotenv()
VK_TOKEN = os.getenv('VK_TOKEN')
GROUP_ID = 241517733

logging.basicConfig(
    # по желанию можно добавить, чтобы записывалось в файл
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

# Авторизация
vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

# Клавиатура с двумя кнопками
keyboard = {
    "one_time": False,
    "buttons": [[
            {
                "action": {"type": "text", "label": "Начать"},
                "color": "positive"
            }],
            [
            {
                "action": {"type": "text", "label": "Хочу котика"},
                "color": "primary"
            }
    ]]
}
keyboard_json = json.dumps(keyboard, ensure_ascii=False)

def make_keyboard(buttons):
    return json.dumps({
        "one_time": False,
        "buttons": [
            [{
                "action": {"type": "text", "label": label},
                "color": color
            }]
            for label, color in buttons
        ]
    }, ensure_ascii=False)

KEYBOARD_START = make_keyboard([
    ("Начать", "positive"),
    ("Хочу котика", "primary"),
])

KEYBOARD_AFTER_START = make_keyboard([
    ("Хочу котика", "primary"),
    ("Вернуть кнопки", "primary"),
])

def get_user_name(vk, user_id):
    user_info = vk.users.get(user_ids=user_id)[0]
    return user_info['first_name']


# Функция для получения случайного URL от API
# def get_new_image():
#     url = 'https://api.thecatapi.com/v1/images/search'
#     response = requests.get(url).json()
#     return response[0].get('url')


def get_new_image():
    source_url = 'https://api.thecatapi.com/v1/images/search'
    try:
        response = requests.get(source_url)
        response = response.json()
        if isinstance(response, list):
            random_image = response[0].get('url')
        elif isinstance(response, dict):
            random_image = response.get('url')
        print(type(response))
    except Exception as error:
        print(error)
        new_url = 'https://dog.ceo/api/breed/affenpinscher/images/random'
        response = requests.get(new_url)
        response = response.json()
        random_image = response.get('message')
    return random_image 

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
        keyboard=KEYBOARD_AFTER_START,
        random_id=random.randint(0, 100000)
    )

def handle_def_buttons(vk, message):
    user_id = message['from_id']
    vk.messages.send(
        user_id=user_id,
        message="Возвращаю кнопки",
        keyboard=KEYBOARD_START,
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
        keyboard=KEYBOARD_AFTER_START,
        random_id=random.randint(0, 100000)
    )


def handle_text(vk, message):
    user_id = message['from_id']
    vk.messages.send(
        user_id=user_id,
        message="Привет, я KittyBot!",
        keyboard=keyboard_json,
        random_id=random.randint(0, 100000)
    )

def main():
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            message = event.object.message
            text = message.get('text', '').strip().lower()
            if text:
                if text == 'начать':
                    handle_start(vk, vk_session, message)
                elif text == 'хочу котика':
                    handle_cat(vk, vk_session, message)
                elif text == 'вернуть кнопки':
                    handle_def_buttons(vk, message)
                else:
                    handle_text(vk, message)

if __name__ == '__main__':
    main()