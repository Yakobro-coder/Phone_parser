import asyncio
import requests
import json
import datetime
from selenium import webdriver
import re


# Ограничение API с ключом доступа пользователя можно обращаться не чаще 3 раз в секунду.
from asinc import async_search_group


class ApiVk:
    """
    Помимо ограничений на частоту обращений, существуют и количественные ограничения на вызов однотипных методов.
    По понятным причинам, мы не предоставляем информацию о точных лимитах.
    После превышения количественного лимита доступ к конкретному методу может требовать ввода капчи (см. captcha_error),

    Код ошибки: 14
    Текст ошибки: Captcha needed

    а также может быть временно ограничен (в таком случае сервер не возвращает ответ на вызов конкретного метода,
    но без проблем обрабатывает любые другие запросы).
    """

    def __init__(self):
        now_data_time = datetime.datetime.now().strftime("%d-%m-%Y_%H.%M")
        self.offset = 0
        self.count = 1000
        self.url = 'https://api.vk.com/method/'
        self.token = self.get_token()
        self.params = {
            'access_token': self.token,
            'v': '5.131'
        }
        self.owner_id = requests.get(self.url + 'users.get', self.params).json()['response'][0]['id']  # user_id

        # Сбор статы used by users
        params_fo_stats = {"response": 1}
        stats_users = requests.get(self.url + 'stats.trackVisitor', params={**self.params, **params_fo_stats}).json()

        try:
            with open("data_base.json", "r", encoding="utf-8") as file:
                self.json_result = json.load(file)
        except FileNotFoundError:
            with open("data_base.json", "a", encoding="utf-8") as file:
                file.write(json.dumps('{}'))
                self.json_result = json.load(file)

        what_search = int(input(' Введите цифру 1 — Поиск людей по параметрам; 2 — Данные участников группы: '))
        if what_search == 1:
            self.search_people()
        elif what_search == 2:
            self.search_group()

    def log_pass(self):
        with open('accounts.txt', encoding='utf-8') as file:
            log_pass = file.readline().split(':')
            return log_pass

    def get_token(self):
        url_authorize = 'https://oauth.vk.com/authorize'
        url_blank = 'https://oauth.vk.com/blank.html'
        app_id = '7903394'
        params = {'client_id': app_id,
                  'redirect_uri': url_blank,
                  'scope': 'offline',
                  'response_type': 'token',
                  'v': '5.131'}

        url_send = requests.get(url_authorize, params=params).url

        driver = webdriver.Firefox()
        driver.get(url_send)

        # получаем лог:пас и txt файла, log_pass[0]-login ну и log_pass[1]-password
        log_pass = self.log_pass()

        # Для удобства сохраняем XPath формы авторизации
        # Заполняем форму авторизации
        username = '//*[@id="login_submit"]/div/div/input[6]'
        driver.find_element_by_xpath(username).send_keys([log_pass[0]])
        # time.sleep(1)

        password_form = '//*[@id="login_submit"]/div/div/input[7]'
        driver.find_element_by_xpath(password_form).send_keys([log_pass[1]])
        # time.sleep(1)

        press_enter = '//*[@id="install_allow"]'
        driver.find_element_by_xpath(press_enter).click()
        # time.sleep(3)

        # Если авторизации ранее уже прошла, скипаем
        if url_blank not in driver.current_url:
            accepting_rules = '//*[@id="oauth_wrap_content"]/div[3]/div/div[1]/button[1]'
            driver.find_element_by_xpath(accepting_rules).click()
            # time.sleep(3)

        result_url = driver.current_url
        # time.sleep(1)

        # Получем токен из урла
        self.token = result_url[result_url.find('=', 0)+1:result_url.find('&', 0)]
        driver.close()

        return self.token

    def search_people(self):
        result = {}
        print()
        print('!!!ВАЖНО!!!')
        print('Если какая то из выборок(видов) поиска не нужна, НИЧЕГО не вводить, нажать просто Enter!')
        print()
        search_str = input('Введите поисковый запрос(не обяз. что бы пропустить, нажать Enter): ')
        print()
        city = input('Введите город: ')
        print()
        sex = input('Пол(1 - женский, 2 - мужской): ')
        print()
        status = input("""Выборка по семейному положению
1 — не женат (не замужем)
2 — встречается
3 — помолвлен(-а)
4 — женат (замужем)
5 — всё сложно
6 — в активном поиске
7 — влюблен(-а)
8 — в гражданском браке
Укажите цифрой семейное полжение: """)
        print()
        age_from = input('Возраст ОТ(впишите число возрастра): ')
        print()
        age_to = input('Возраст ДО(впишите число возрастра): ')
        print()
        online = input('Учитывать ли статус «онлайн»(1 — искать только пользователей онлайн): ')
        print()
        has_photo = input('Учитывать ли наличие фото(1 — искать только с фотографией): ')
        print()

        if age_from == 0:
            age_from = ''
        if age_to == 0:
            age_to = ''

        params = {'q': search_str,
                  'count': 1000,
                  'fields': 'id, first_name, last_name, contacts',
                  'hometown': city,
                  'sex': sex,
                  'status': status,
                  'age_from': age_from,
                  'age_to': age_to,
                  'online': online,
                  'has_photo': has_photo
                  }
        search = requests.get(self.url + 'users.search', params={**self.params, **params}).json()
        if search['response'].get('count') > 1000:
            print('*' * 60)
            print("""API VK ограниченно выводом по поисковому запросу НЕ БОЛЕЕ 1000 человек!!!
Либо измените запрос, что бы уменьшить количество найденных людей менее 1000...
Либо меняйте каждый раз запросы и обрабатывайте первые 1000 человек""")
        print('*' * 60)
        print(f"Обработано 1000 из {search['response'].get('count')} человек.")
        print('-' * 33)
        for user in search['response']['items']:
            if 'mobile_phone' in user:
                mobil = user.get('mobile_phone')
                home_phone = user.get('home_phone')
                first_name = user.get('first_name')
                last_name = user.get('last_name')
                id_user = user.get('id')

                res_mobil = ''.join(re.findall('[+\d\s-]', str(mobil))).strip()
                if res_mobil != '':
                    if len(res_mobil) >= 7:
                        print_mobil = res_mobil
                    else:
                        print_mobil = None
                else:
                    print_mobil = None

                res_home = ''.join(re.findall('[+\d\s-]', str(home_phone))).strip()
                if res_home != '':
                    if len(res_home) > 4:
                        print_home = res_home
                    else:
                        print_home = None
                else:
                    print_home = None

                finish_print = ''
                if print_mobil is not None and print_home is None:
                    finish_print = f'{first_name} {last_name}: моб. - {print_mobil}'
                elif print_mobil is None and print_home is not None:
                    finish_print = f'{first_name} {last_name}: дом. - {print_home}'
                elif print_mobil is not None and print_home is not None:
                    finish_print = f'{first_name} {last_name}: моб. - {print_mobil}, дом. - {print_home}'

                # Запись строкой в словарь
                if finish_print != '':
                    self.json_result.update({id_user: finish_print})

        with open("data_base.json", "w", encoding="utf-8") as file:
            file.write(json.dumps(self.json_result, indent=4, ensure_ascii=False))

        start = True
        while start:
            what_next = input('Продолжить парсить? Введите цифру 1 что бы продолжить, а если хватит, то цифру 2: ')
            if what_next == '1':
                return self.search_people()
            elif what_next == '2':
                start = False
            else:
                print('Вы ввели что то некорректно... Ещё раз....')

    def search_group(self):
        url = "https://api.vk.com/method/execute?"
        id_group = input('Укажите идентификатор(id) или короткое имя сообщества: ')

        params = {'group_id': id_group,
                  'count': 0}
        count_id = requests.get(self.url + 'groups.getMembers', params={**self.params, **params}).json()['response']['count']

        # Async search phone numbers
        self.json_result, start = asyncio.run(async_search_group(id_group, count_id, self.token, self.json_result))

        while start:
            what_next = input('Продолжить парсить другие группы? '
                              'Введите цифру 1 что бы продолжить, а если хватит, то цифру 2: ')
            if what_next == '1':
                return self.search_group()
            elif what_next == '2':
                start = False
            else:
                print('Вы ввели что то некорректно... Ещё раз....')


if __name__ == '__main__':
    ApiVk()

