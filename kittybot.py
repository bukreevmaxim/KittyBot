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
from logging.handlers import RotatingFileHandler

load_dotenv()
VK_TOKEN = os.getenv('VK_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')

# logging.basicConfig(
#     # по желанию можно добавить, чтобы записывалось в файл
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     filename='main.log',
#     filemode='a',
#     level=logging.INFO,
# )

vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Указываем обработчик логов:
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler = RotatingFileHandler(
    'my_logger.log',
    maxBytes=50000000,
    backupCount=5
    )
handler.setFormatter(formatter)
logger.addHandler(handler)

keyboard = {
    "one_time": False,
    "buttons": [[
            {
                "action": {"type": "text", "label": "Начать"},
                "color": "positive"
            },
            {
                "action": {"type": "text", "label": "Хочу котика"},
                "color": "primary"
            }
    ]]
}
keyboard_json = json.dumps(keyboard, ensure_ascii=False)


def get_user_name(vk, user_id):
    user_info = vk.users.get(user_ids=user_id)[0]
    return user_info['first_name']


def get_new_image():
    source_url = 'https://aleatori.cat/random.json'
    try:
        response = requests.get(source_url)
        response = response.json()
        random_image = response[0].get('url')
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        new_url = 'https://dog.ceo/api/breed/affenpinscher/images/random'
        response = requests.get(new_url)
        response = response.json()
        random_image = response.get('message')
    return random_image


def upload_image(vk_session, peer_id, image_url):
    upload_url = vk_session.method('photos.getMessagesUploadServer', {'peer_id': peer_id})['upload_url']
    img_data = requests.get(image_url).content
    files = {'photo': ('cat.jpg', io.BytesIO(img_data))}
    response = requests.post(upload_url, files=files)
    result = response.json()
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

    image_url = get_new_image()
    attachment = upload_image(vk_session, peer_id, image_url)
    vk.messages.send(
        user_id=user_id,
        attachment=attachment,
        message=f"Привет, {name}. Посмотри, какого котика я тебе нашёл",
        keyboard=keyboard_json,
        random_id=random.randint(0, 100000)
    )

def handle_cat(vk, vk_session, message):
    user_id = message['from_id']
    peer_id = message['peer_id']

    image_url = get_new_image()
    attachment = upload_image(vk_session, peer_id, image_url)
    vk.messages.send(
        user_id=user_id,
        attachment=attachment,
        keyboard=keyboard_json,
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
                else:
                    handle_text(vk, message)


if __name__ == '__main__':
    main()