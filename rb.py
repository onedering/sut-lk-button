import requests
from bs4 import BeautifulSoup
import yaml
import os
from logger import log_message
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

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
    log_message("Создание конфигурационного файла")
    print('Конфигурационный файл не найден. Пожалуйста, введите данные для авторизации.')
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
    Функция авторизации на портале через requests.
    Возвращает True, если авторизация прошла успешно.
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
    session.get(url_lk)
    response = session.post(url_auth, data=data)
    soup = BeautifulSoup(response.text, 'lxml')
    if soup.p and soup.p.text == '1':
        session.get(url_lk)
        return True
    return False

def start_lesson():
    """
    Функция для авторизации через Selenium, перехода к расписанию и нажатия кнопки "Начать занятие".
    Пример кнопки:
    <span id="knop970285"><a onclick="open_zan(970285,27);">Начать занятие</a></span>
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--headless")  # Режим headless; для отладки можно убрать эту опцию
    # Скрытие лишних сообщений в консоли
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--log-level=3")
    
    driver = webdriver.Chrome(options=options)
    timeout = 600           # Общее время ожидания (в секундах)
    refresh_interval = 120   # Интервал обновления страницы (в секундах)

    try:
        driver.get("https://lk.sut.ru/")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "users"))
        )
        config = load_config()
        login_input = driver.find_element(By.NAME, "users")
        password_input = driver.find_element(By.NAME, "parole")
        login_input.send_keys(config["LOGIN"])
        password_input.send_keys(config["PASSWORD"])
        login_button = driver.find_element(By.ID, "logButton")
        login_button.click()

        # Ожидание успешной авторизации (меню "Учеба..." должно стать кликабельным)
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@data-target='#collapse1']"))
        )

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Открываем меню "Учеба..."
                study_menu = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@data-target='#collapse1']"))
                )
                study_menu.click()
                
                # Ждём раскрытия меню
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='collapse1' and contains(@class, 'show')]"))
                )
                # Переходим к пункту "Расписание"
                schedule_link = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@title='Расписание']"))
                )
                schedule_link.click()

                # Поиск кнопки "Начать занятие"
                button = WebDriverWait(driver, refresh_interval).until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Начать занятие')]"))
                )
                log_message("Кнопка 'Начать занятие' найдена, выполняется нажатие.")
                # Логируем HTML-код найденной кнопки
                button_html = button.get_attribute('outerHTML')
                log_message(f"Код кнопки: {button_html}")
                driver.execute_script("arguments[0].click();", button)
                log_message("Нажатие кнопки 'Начать занятие' выполнено.")
                return  # Прерываем дальнейший поиск после успешного нажатия
            except TimeoutException:
                log_message("Кнопка не найдена, обновляю страницу...")
                driver.refresh()
        
        log_message("Кнопка 'Начать занятие' не найдена в течение заданного времени.")
    except Exception as e:
        log_message(f"Ошибка при выполнении start_lesson: {str(e)}")
    finally:
        driver.quit()
