import requests
from bs4 import BeautifulSoup
import yaml
import os
from logger import log_message
import rb

CONFIG_FILE = "creds.yaml"

def main():
    config = rb.load_config()

    if not config:
        config = rb.create_config()

    if rb.auth_lk(config):
        log_message("Авторизация прошла успешно.")
        if rb.find_button():
            rb.start_lesson()
        else:
            log_message("Кнопка для начала занятия не найдена.")
    else:
        log_message("Авторизация не пройдена. Проверьте логин/пароль.")
        print("Авторизация не пройдена. Проверьте логин/пароль.")
        retry = input("Хотите обновить данные? (да/нет): ").strip().lower()
        if retry in ["да", "y", "yes"]:

            os.remove(CONFIG_FILE)  # Удаляем старый файл конфигурации
            main()  # Перезапускаем процесс
        else:
            log_message("Завершение программы.")

if __name__ == "__main__":
    main()