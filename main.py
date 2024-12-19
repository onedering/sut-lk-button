import os
import time
import schedule  # Для планирования задач
from logger import log_message
import rb

CONFIG_FILE = "creds.yaml"

def auth():
    config = rb.load_config()

    if not config:
        config = rb.create_config()

    if rb.auth_lk(config):
        log_message("Авторизация прошла успешно.")
        
    else:
        log_message("Авторизация не пройдена. Проверьте логин/пароль.")
        print("Авторизация не пройдена. Проверьте логин/пароль.")
        retry = input("Хотите обновить данные? (да/нет): ").strip().lower()
        if retry in ["да", "y", "yes"]:
            os.remove(CONFIG_FILE)  # Удаляем старый файл конфигурации
            auth()  # Перезапускаем процесс
        else:
            log_message("Завершение программы.")


# Функция для расписания
def schedule_main():
    # Добавляем задачи в расписание
    
    
    schedule.every().day.at("09:00").do(log_and_run, "1-я пара: 09:00-10:35")
    schedule.every().day.at("10:45").do(log_and_run, "2-я пара: 10:45-12:20")
    schedule.every().day.at("13:00").do(log_and_run, "3-я пара: 13:00-14:35")
    schedule.every().day.at("14:45").do(log_and_run, "4-я пара: 14:45-16:20")
    schedule.every().day.at("16:30").do(log_and_run, "5-я пара: 16:30-18:05")
    schedule.every().day.at("18:15").do(log_and_run, "6-я пара: 18:15-19:50")
    schedule.every().day.at("20:00").do(log_and_run, "7-я пара: 20:00-21:35")

    log_message("Запланированы задачи для всех пар.")
    
    # Бесконечный цикл для выполнения задач по расписанию
    while True:
        schedule.run_pending()  # Выполняет задачи, если наступило время
        time.sleep(1)  # Ждём 1 секунду перед проверкой расписания

def log_and_run(pair_info):
    """
    Логирование пары и запуск main
    """
    log_message(f"Начало {pair_info}")
    rb.start_lesson()

if __name__ == "__main__":
    log_message("")
    log_message("Запуск программы...")
    auth()
    schedule_main()
    log_message("Завершение программы.")
