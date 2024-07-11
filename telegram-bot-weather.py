import io
import json
import os
import requests
from datetime import datetime


def get_weather_data(place: str, token: str) -> dict:
    """Получение текущей температуры для заданного места

    :param place: Место (название населенного пункта)
    :param token: Токен для OpenWeather API
    :return: Температура в градусах Цельсия
    """
    # https://openweathermap.org/current
    # Сформируем URL для обращения к API OpenWeather.
    url = "https://api.openweathermap.org/data/2.5/weather"
    # Сформируем параметры для обращения к API OpenWeather.
    parameters = {"q": place, "appid": token, "lang": "ru", "units": "metric"}
    # Выполним запрос к API OpenWeather.
    response = requests.get(url=url, params=parameters).json()
    # https://openweathermap.org/current#fields_json
    # Из ответа получим значение текущей температуры.

    weather_description = response["weather"][0]["description"]
    temp = response["main"]["temp"]
    feels_like = response["main"]["feels_like"]
    pressure = response["main"]["pressure"]
    humidity = response["main"]["humidity"]
    visibility = response["visibility"]
    wind_speed = response["wind"]["speed"]
    wind_deg = response["wind"]["deg"]

    sunrise_timestamp = response["sys"]["sunrise"]
    sunset_timestamp = response["sys"]["sunset"]
    sunrise = datetime.fromtimestamp(sunrise_timestamp).strftime('%H:%M')
    sunset = datetime.fromtimestamp(sunset_timestamp).strftime('%H:%M')

    wind_direction = {
        0: "С",
        45: "СВ",
        90: "В",
        135: "ЮВ",
        180: "Ю",
        225: "ЮЗ",
        270: "З",
        315: "СЗ",
    }
    wind_direction_key = (wind_deg + 22.5) % 360
    wind_direction_key = int(wind_direction_key // 45)
    wind_direction_value = wind_direction[wind_direction_key]

    return {
        "weather_description": weather_description,
        "temp": temp,
        "feels_like": feels_like,
        "pressure": pressure,
        "humidity": humidity,
        "visibility": visibility,
        "wind_speed": wind_speed,
        "wind_direction": wind_direction_value,
        "sunrise": sunrise,
        "sunset": sunset,
    }


def send_message(text: str, chat_id: str, message_id: str, token: str):
    """Отправка текстового сообщения пользователю Telegram

    :param text: Текст сообщения для отправки
    :param chat_id: Идентификатор чата
    :param message_id: Идентификатор входящего сообщения
    :param token: Токен для Telegram Bot API
    """
    # https://core.telegram.org/bots/api#replyparameters
    # Сформируем объект ReplyParameters из Telegram Bot API
    reply_parameters = {"message_id": message_id}

    # https://core.telegram.org/bots/api#sendmessage
    # Сформируем URL для обращения к методу sendMessage из Telegram Bot API
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    # Сформируем параметры для метода sendMessage из Telegram Bot API
    parameters = {"chat_id": chat_id, "text": text,
                  "reply_parameters": reply_parameters}

    # POST запросом вызовем метод sendMessage Telegram Bot API.
    # Параметры передадим в виде JSON в теле HTTP-запроса.
    requests.post(url=url, json=parameters)


def send_voice(voice: bytes, chat_id: str, message_id: str, token: str):
    """Отправка голосового сообщения пользователю Telegram.

    :param voice: Двоичные данные с голосовым сообщением
    :param chat_id: Идентификатор чата
    :param message_id: Идентификатор входящего сообщения
    :param token: Токен для Telegram Bot API
    """
    # Преобразуем двоичные данные с голосовым сообщением в file-like объект
    voice_file = io.BytesIO(voice)

    # https://core.telegram.org/bots/api#sendvoice
    # Сформируем URL для обращения к методу sendVoice из Telegram Bot API
    url = f"https://api.telegram.org/bot{token}/sendVoice"
    # Сформируем параметры для метода sendVoice из Telegram Bot API
    parameters = {"chat_id": chat_id}

    # POST запросом вызовем метод sendVoice Telegram Bot API.
    # Параметры передадим в виде URL query string HTTP-запроса.
    # Двоичные данные с голосовым сообщением передадим в теле HTTP-запроса
    # как multipart/form-data
    requests.post(url=url, data=parameters, files={"voice": voice_file})


def download_file(file_id: str, token: str) -> bytes:
    """Получение файла с серверов Telegram Bot API

    :param file_id: Идентификатор файла
    :param token: Токен для Telegram Bot API
    :return: Двоичный объект файла
    """
    # https://core.telegram.org/bots/api#getfile
    # Сформируем URL для обращения к методу getFile из Telegram Bot API
    url = f"https://api.telegram.org/bot{token}/getFile"
    # Сформируем параметры для метода getFile из Telegram Bot API
    parameters = {"file_id": file_id}

    # https://core.telegram.org/bots/api#making-requests
    # POST запросом вызовем метод getFile Telegram Bot API.
    # Параметры передадим в виде JSON в теле HTTP-запроса.
    response = requests.post(url=url, json=parameters).json()

    # Из ответа извлечен объект File
    file = response["result"]
    # Из объекта File извлечен путь до файла
    file_path = file["file_path"]
    # Сформируем URL для получения файла
    download_url = f"https://api.telegram.org/file/bot{token}/{file_path}"

    # Получим файл
    download_response = requests.get(url=download_url)

    # Извлечем из ответа на HTTP-запрос содержимое файла
    file_content = download_response.content

    return file_content


def stt(voice: bytes, token: str) -> str:
    """Распознавание речи из аудио данных

    :param voice: Двоичные данные записи речи
    :param token: Токен для доступа к API Yandex Cloud
    :return:
    """
    # https://yandex.cloud/ru/docs/speechkit/stt/api/request-api
    # Сформируем URL для обращения к API синхронного распознавания.
    url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
    # https://yandex.cloud/ru/docs/speechkit/concepts/auth
    # Подготовим аутентификацию к API синхронного распознавания.
    auth = {"Authorization": f"Bearer {token}"}

    # Выполним запрос к API синхронного распознавания.
    # Двоичное содержимое аудио файла отправим в теле HTTP-запроса.
    response = requests.post(url=url, headers=auth, data=voice).json()

    # Из ответа извлечем распознанный текст
    text = response["result"]

    return text


def tts(text: str, token: str) -> bytes:
    """Синтез речи по тексту

    :param text: Текст для синтеза речи
    :param token: Токен для доступа к API Yandex Cloud
    :return: Двоичные данные синтезированной речи
    """
    # https://yandex.cloud/ru/docs/speechkit/tts/request
    # Сформируем URL для обращения к API синтеза речи.
    url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
    # Подготовим параметры для обращения к API синтеза речи.
    params = {"text": text, "voice": "ermil", "emotion": "good"}
    # https://yandex.cloud/ru/docs/speechkit/concepts/auth
    # Подготовим аутентификацию для доступа к API синтеза речи.
    auth = {"Authorization": f"Bearer {token}"}

    # Выполним запрос к API синтеза речи.
    # Параметры передадим в теле запроса.
    yc_tts_response = requests.post(url=url, data=params, headers=auth)

    # Извлечем из ответа содержимое аудио данных с синтезированной речью
    voice = yc_tts_response.content

    return voice


def handler(event, context):
    """Обработчик облачной функции. Реализует Webhook для Telegram Bot.

    :param event: Упакованный HTTP-запрос
    :param context: Контекст исполнения облачной функции
    """
    # Этот словарь будем возвращать, как результат облачной функции.
    yc_function_response = {'statusCode': 200, 'body': ''}
    # Получим токен для Telegram Bot API
    tg_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    # Получим токен для OpenWeather API
    ow_token = os.environ.get("WEATHER_TOKEN")
    # https://yandex.cloud/ru/docs/functions/lang/python/context.
    # Получим токен для сервисов Yandex Cloud из контекста облачной функции
    # Для других языков программирования смотрите соответствующие разделы.
    yc_token = context.token["access_token"]

    # https://yandex.cloud/ru/docs/functions/concepts/function-invoke#request
    # В аргументе event передается JSON с данными об HTTP-запросе.
    # По ключу body содержится тело HTTP-запроса.
    # Сервер Telegram Bot API при использовании Webhook передает
    # в теле HTTP-запроса объект Update в JSON формате.
    # Извлечем объект Update
    update = json.loads(event['body'])

    # https://core.telegram.org/bots/api#update
    # Извлечем объект Message.
    message = update['message']

    # https://core.telegram.org/bots/api#message
    # Извлечем id чата и id поступившего сообщения.
    message_id = message["message_id"]
    chat_id = message["chat"]["id"]

     # Обработка команд /start и /help
    if "text" in message and message["text"].startswith("/"):
        if message["text"] in ("/start", "/help"):
            send_message(text="Я расскажу о текущей погоде для населенного пункта.\n\nЯ могу ответить на:\n- Текстовое сообщение с названием населенного пункта.\n- Голосовое сообщение с названием населенного пункта.\n- Сообщение с геопозицией.", chat_id=chat_id, message_id=message_id, token=tg_token)
            return yc_function_response

    # Обработка текстового входящего сообщения
    if "text" in message:
        place = message["text"]
        weather_data = get_weather_data(place=place, token=ow_token)
        if weather_data:
            text = f"{weather_data['weather_description']}.\nТемпература {weather_data['temp']:.1f} ℃, ощущается как {weather_data['feels_like']:.1f} ℃.\nАтмосферное давление {weather_data['pressure']} мм рт. ст.\nВлажность {weather_data['humidity']} %.\nВидимость {weather_data['visibility']} метров.\nВетер {weather_data['wind_speed']:.1f} м/с {weather_data['wind_direction']}.\nВосход солнца {weather_data['sunrise']} МСК. Закат {weather_data['sunset']} МСК."
            send_message(text=text, chat_id=chat_id, message_id=message_id,
                        token=tg_token)
        else:
            send_message(text="Я не знаю какая погода в этом месте.", chat_id=chat_id, message_id=message_id, token=tg_token)
        return yc_function_response

    # Обработка голосового входящего сообщения
    if "voice" in message:
        voice = message["voice"]

        if voice["duration"] > 30:
            error_text = "Голосовое сообщение должно быть короче 30 секунд"
            send_message(text=error_text, chat_id=chat_id,
                         message_id=message_id, token=tg_token)
            return yc_function_response
        
        voice_content = download_file(file_id=voice["file_id"], token=tg_token)
        place = stt(voice=voice_content, token=yc_token)
        weather_data = get_weather_data(place=place, token=ow_token)
        if weather_data:
            text = f"Населенный пункт {place}.\n{weather_data['weather_description']}.\nТемпература {weather_data['temp']:.0f} градусов цельсия.\nОщущается как {weather_data['feels_like']:.0f} градусов цельсия.\nДавление {weather_data['pressure']} миллиметров ртутного столба.\nВлажность {weather_data['humidity']} процентов."
            yc_tts_voice = tts(text=text, token=yc_token)
            send_voice(voice=yc_tts_voice, message_id=message_id, chat_id=chat_id,
                    token=tg_token)
        else: 
            send_voice(text="Я не знаю какая погода в этом месте.", chat_id=chat_id, message_id=message_id, token=tg_token)
        return yc_function_response


    # Обработка сообщений с геопозицией
    if "location" in message:
        latitude = message["location"]["latitude"]
        longitude = message["location"]["longitude"]
        weather_data = get_weather_data(place=f"{latitude},{longitude}", token=ow_token)
        if weather_data:
            weather_text = f"{weather_data['weather_description']}.\nТемпература {weather_data['temp']:.1f} ℃, ощущается как {weather_data['feels_like']:.1f} ℃.\nАтмосферное давление {weather_data['pressure']} мм рт. ст.\nВлажность {weather_data['humidity']} %.\nВидимость {weather_data['visibility']} метров.\nВетер {weather_data['wind_speed']:.1f} м/с {weather_data['wind_direction']}.\nВосход солнца {weather_data['sunrise']} МСК. Закат {weather_data['sunset']} МСК."
            send_message(text=weather_text, chat_id=chat_id, message_id=message_id, token=tg_token)
        else:
            send_message(text="Я не знаю какая погода в этом месте.", chat_id=chat_id, message_id=message_id, token=tg_token)
        return yc_function_response
    
    error_text = "Я не могу ответить на такой тип сообщения. /nНо могу ответить на: /n- Текстовое сообщение с названием населенного пункта /n- Голосовое сообщение с названием населенного пункта./n- Сообщение с геопозицией."
    send_message(text=error_text, chat_id=chat_id, message_id=message_id,
                 token=tg_token)
    return yc_function_response