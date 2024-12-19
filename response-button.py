import requests
from bs4 import BeautifulSoup
import yaml
import os
from logger import log_message

CONFIG_FILE = "creds.yaml"
session = requests.Session()

def load_config():
    """
    Загружает существующий конфигурационный файл.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return yaml.safe_load(file)
    else:
        return None

def create_config():
    """
    Создает конфигурационный файл.
    """
    log_message("Конфигурационный файл не найден. Пожалуйста, введите данные для авторизации.")
    config = {
        "LOGIN": input("Введите ваш логин: ").strip(),
        "PASSWORD": input("Введите ваш пароль: ").strip()
    }
    with open(CONFIG_FILE, "w") as file:
        yaml.dump(config, file)
    log_message(f"Конфигурация сохранена в файл {CONFIG_FILE}.")
    return config

def auth_lk(config):
    """
    Функция авторизации на портале. Возвращает True, если авторизация прошла успешно.
    """
    url_lk = 'https://lk.sut.ru/?login=yes'
    url_auth = 'https://lk.sut.ru/cabinet/lib/autentificationok.php'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
    }
    data = {
        'users': config["LOGIN"],
        'parole': config["PASSWORD"],
    }
    session.headers.update(headers)
    # Инициализируем сессию
    session.get(url_lk)
    # Отправляем запрос авторизации
    response = session.post(url_auth, data=data)
    soup = BeautifulSoup(response.text, 'lxml')
    # Повторный заход на ЛК
    session.get(url_lk)
    return soup.p.text == '1'

def find_button():
    """
    Функция для поиска кнопки "начать занятие" на странице.
    """
    # TODO: Реализовать поиск кнопки
    return False

def start_lesson():
    """
    Функция для начала занятия.
    """
    # TODO: Реализовать логику начала занятия
    pass

def main():
    config = load_config()

    if not config:
        config = create_config()

    if auth_lk(config):
        log_message("Авторизация прошла успешно.")
        if find_button():
            start_lesson()
        else:
            log_message("Кнопка для начала занятия не найдена.")
    else:
        log_message("Авторизация не пройдена. Проверьте логин/пароль.")
        retry = input("Хотите обновить данные? (да/нет): ").strip().lower()
        if retry == "да":
            os.remove(CONFIG_FILE)  # Удаляем старый файл конфигурации
            main()  # Перезапускаем процесс
        else:
            log_message("Завершение программы.")

if __name__ == "__main__":
    main()
