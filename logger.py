from datetime import datetime

def log_message(message):
    """
    Логирует сообщение с текущим временем.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('logs/sync.log', 'a') as log:
        log.write(f'[{timestamp}] {message}\n')
