import requests
from bs4 import BeautifulSoup
import yaml
import os
from logger import log_message
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
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
    session.get(url_lk)
    response = session.post(url_auth, data=data)
    soup = BeautifulSoup(response.text, 'lxml')
    if soup.p and soup.p.text == '1':
        session.get(url_lk)
        return True
    return False

def find_button():
    """
    Функция для поиска кнопки "начать занятие" через Selenium.
    """
    #log_message("Инициализация WebDriver для поиска кнопки.")
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")  # Игнорировать SSL ошибки
    options.add_argument("--headless")  # Уберите эту строку, если нужно видеть браузер
    driver = webdriver.Chrome(options=options)
    timeout=300  #общее время ожидания (в секундах)
    refresh_interval=30 #интервал обновления страницы (в секундах)


    try:
        driver.get("https://lk.sut.ru/")
        log_message("Загрузка страницы авторизации.")

        # Авторизация через Selenium
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "users")))
        login_input = driver.find_element(By.NAME, "users")
        password_input = driver.find_element(By.NAME, "parole")
        login_input.send_keys(load_config()["LOGIN"])
        password_input.send_keys(load_config()["PASSWORD"])
        #password_input.send_keys(Keys.RETURN)

        # Нажатие кнопки "Войти"
        login_button = driver.find_element(By.ID, "logButton")
        login_button.click()
        #log_message("Кнопка 'Войти' нажата.")

        # Ожидание подтверждения авторизации через проверку конкретного элемента
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@data-target='#collapse1']"))
        )
        log_message("Авторизация подтверждена.")

        
        
        # Поиск кнопки "Начать занятие"
        start_time = time.time()
        log_message("Начало ожидания кнопки 'Начать занятие' с обновлением страницы.")

        while time.time() - start_time < timeout:
            try:
                # Открытие меню "Учеба..."
                study_menu = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@data-target='#collapse1']"))
                )
                study_menu.click()
                #log_message("Меню 'Учеба...' открыто.")

                # Ожидание раскрытия списка
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='collapse1' and contains(@class, 'show')]"))
                )

                # Переход к пункту "Расписание"
                schedule_link = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@title='Расписание']"))
                )
                schedule_link.click()
                #log_message("Открыта страница расписания.")

                # Поиск кнопки
                button = WebDriverWait(driver, refresh_interval).until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Начать занятие')]"))
                )
                log_message("Кнопка 'Начать занятие' найдена.")
                return button
            except TimeoutException:
                # Обновляем страницу, если кнопка не найдена в течение refresh_interval
                log_message("Кнопка не найдена, обновляю страницу...")
                driver.refresh()

        #log_message("Кнопка 'Начать занятие' не найдена в течение заданного времени.")
        return None
    
    except Exception as e:
        log_message(f"Ошибка при поиске кнопки: {str(e)}")
        return None

    finally:
        driver.quit()

def start_lesson():
    """
    Функция для нажатия кнопки "Начать занятие".
    """
    log_message("Попытка начать занятие.")
    button = find_button()
    if button:
        log_message("Нажатие кнопки 'Начать занятие'.")
        ActionChains(button.parent).move_to_element(button).click(button).perform()
    else:
        log_message("Кнопка 'Начать занятие' не найдена.")