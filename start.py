import os
import time
import schedule  # Для планирования задач
import threading
import ctypes
import win32gui, win32con
from logger import log_message
import rb
from pystray import Icon, MenuItem, Menu
from PIL import Image

CONFIG_FILE = "creds.yaml"
is_authenticated = False

def get_console_window():
    # Используем ctypes для получения дескриптора консольного окна
    return ctypes.windll.kernel32.GetConsoleWindow()

def auth():
    global is_authenticated
    config = rb.load_config()
    if not config:
        config = rb.create_config()

    if rb.auth_lk(config):
        log_message("Авторизация прошла успешно.")
        is_authenticated = True
        minimize_to_tray()  # При успешной авторизации сразу сворачиваем окно в трей
    else:
        log_message("Авторизация не пройдена. Проверьте логин/пароль.")
        print("Авторизация не пройдена. Проверьте логин/пароль.")
        retry = input("Хотите обновить данные? (да/нет): ").strip().lower()
        if retry in ["да", "y", "yes"]:
            os.remove(CONFIG_FILE)  # Удаляем старый файл конфигурации
            auth()  # Перезапускаем процесс
        else:
            log_message("Завершение программы.")

def monitor_window():
    """
    Мониторит состояние окна консоли и прячет его в трей, если оно свернуто.
    """
    hwnd = get_console_window()
    while True:
        if win32gui.IsIconic(hwnd):  # Если окно свернуто
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        time.sleep(1)

def minimize_to_tray():
    """
    Сворачивает окно консоли в трей, запускает мониторинг состояния окна,
    а также создает иконку в трее с меню для восстановления или завершения.
    """
    hwnd = get_console_window()
    win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
    
    # Запускаем поток для постоянного мониторинга состояния окна
    monitor_thread = threading.Thread(target=monitor_window, daemon=True)
    monitor_thread.start()
    
    # Создаем иконку для системного трея
    image = Image.new("RGB", (64, 64), (0, 0, 0))  # Простая черная иконка (можно заменить своей)
    menu = Menu(
        MenuItem("Развернуть", restore_window),
        MenuItem("Выход", exit_app)
    )
    icon = Icon("lesson_scheduler", image, "Уведомления", menu)
    icon.run()

def restore_window(icon, item):
    """
    Разворачивает окно из трея.
    """
    hwnd = get_console_window()
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    icon.stop()  # Останавливаем иконку трея

def exit_app(icon, item):
    """
    Завершает приложение.
    """
    log_message("Приложение закрыто через трей.")
    icon.stop()
    os._exit(0)

def schedule_main():
    schedule.every().day.at("09:00").do(log_and_run, "1-я пара: 09:00-10:35")
    schedule.every().day.at("10:45").do(log_and_run, "2-я пара: 10:45-12:20")
    schedule.every().day.at("13:00").do(log_and_run, "3-я пара: 13:00-14:35")
    schedule.every().day.at("14:45").do(log_and_run, "4-я пара: 14:45-16:20")
    schedule.every().day.at("16:30").do(log_and_run, "5-я пара: 16:30-18:05")
    schedule.every().day.at("18:15").do(log_and_run, "6-я пара: 18:15-19:50")
    schedule.every().day.at("20:00").do(log_and_run, "7-я пара: 20:00-21:35")
    log_message("Запланированы задачи для всех пар.")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

def log_and_run(pair_info):
    log_message(f"Начало {pair_info}")
    rb.start_lesson()

if __name__ == "__main__":
    log_message("Запуск программы...")
    auth()
    
    if is_authenticated:
        log_and_run("Первый запуск")
        schedule_main()
    
    log_message("Завершение программы.")
