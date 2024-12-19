from datetime import datetime
import os

def log_message(message):
    """
    Логирует сообщение с текущим временем.
    """
    if not os.path.exists('logs'):
        os.makedirs('logs')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('logs/rb.log', 'a', encoding='utf-8') as log:
        log.write(f'[{timestamp}] {message}\n')
