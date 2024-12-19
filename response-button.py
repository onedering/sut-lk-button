import requests
from bs4 import BeautifulSoup

# Предположим, что у нас есть глобальные переменные LOGIN и PASSWORD
LOGIN = "ВАШ_ЛОГИН"    # TODO: заменить на ваш логин
PASSWORD = "ВАШ_ПАРОЛЬ" # TODO: заменить на ваш пароль

session = requests.Session()

def auth_lk():
    """
    Функция авторизации на портале.
    Возвращает True, если авторизация прошла успешно.
    """
    url_lk = 'https://lk.sut.ru/?login=yes'
    url_auth = 'https://lk.sut.ru/cabinet/lib/autentificationok.php'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
    }
    data = {
        'users': LOGIN,
        'parole': PASSWORD,
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

if auth_lk():
    print("Авторизация прошла успешно.")
else:
    print("Авторизация не пройдена. Проверьте логин/пароль.")
    exit()

# После авторизации переходим к странице расписания
url_schedule = "https://lk.sut.ru/cabinet/project/cabinet/forms/raspisanie.php"
response = session.get(url_schedule)
response.encoding = 'windows-1251'  # Судя по content-type, может потребоваться
soup = BeautifulSoup(response.text, 'lxml')

# TODO: Найти кнопку "начать занятие".
# В вашем HTML-примере нет явной кнопки "начать занятие".
# Предположим, что кнопка появляется динамически или в другом месте.
# Нужно знать либо идентификатор этой кнопки, либо данные, которые она отправляет.

# Допустим, что при нажатии на кнопку отправляется POST-запрос с параметрами:
# lesson_id = XXX
# action = "start"
# Это выдумано для примера. Вам надо заменить эти данные на реальные.

# Пример поиска нужного занятия в HTML (если там есть примечание о том, что занятие скоро начнется):
# rows = soup.select("table.simple-little-table tr")
# for row in rows:
#     # Ищем фразу "начать занятие"
#     # Предположим, что где-то в одной из ячеек будет ссылка или кнопка с текстом
#     link = row.find("a", text="Ссылка")  # Пример - ищем ссылку на занятие
#     if link:
#         # TODO: Определить параметры занятия (id, время и т.д.)
#         lesson_id = "ЗАГЛУШКА"  # TODO: узнать реальный ID занятия
#         break

# Поскольку у нас нет точных данных, ниже приводится шаблон кода запроса.
# Предположим, что для начала занятия нужно отправить POST-запрос на тот же URL или другой (например):
url_start_lesson = "https://lk.sut.ru/cabinet/project/cabinet/forms/raspisanie.php"

# Возможно, требуется CSRF-токен:
# csrf_token = ... # TODO: Получить из скрытого поля формы, если таковой имеется.

data = {
    # TODO: заполнить реальными параметрами, например:
    # 'lesson_id': lesson_id,
    # 'action': 'start',
    # 'csrf_token': csrf_token, # если нужен
}

headers = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    # Остальные заголовки можно взять из вашего лога
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Referer': 'https://lk.sut.ru/cabinet/?login=yes',
    'Accept': 'text/plain, */*; q=0.01'
}

# Отправляем POST-запрос, который должен имитировать нажатие на кнопку "начать занятие"
# При условии, что у нас есть все необходимые параметры.
if data:  # проверяем, что данные заполнены
    start_response = session.post(url_start_lesson, data=data, headers=headers)
    if start_response.status_code == 200:
        print("Запрос на начало занятия отправлен.")
        # TODO: Проверить ответ, чтобы убедиться, что занятие действительно началось.
        # Например, посмотреть содержимое start_response.text
    else:
        print(f"Ошибка при отправке запроса. Код: {start_response.status_code}")
else:
    print("Данные для начала занятия не заполнены. Дополните код нужными параметрами.")
