import asyncio
import aiohttp
import json
import re
import time
from tqdm import tqdm
from more_itertools import chunked


async def async_search_group(id_group, count_id, token, self_json,):

    json_result = self_json

    print(count_id)
    print()
    count_ring = (count_id // 25000) + 1
    offset = 0

    coroutines = []
    pbar = tqdm(total=count_ring)
    for i in range(0, count_ring):
        code = 'var i = 0;\n' \
               'var members = [];\n' \
               f'var offset = {offset};\n' \
               'while(i < 25){members = members + API.groups.getMembers({' \
               f'"group_id": "{id_group}", "offset": offset, "fields": "id, first_name, last_name, contacts"' \
               '}).items;\n' \
               'i = i + 1;\n' \
               'offset = offset + 1000;}\n' \
               'return members;'

        params = dict(code=code, access_token=token, v='5.131')

        # Create coroutines
        get_phone_users = search(params)
        coroutines.append(get_phone_users)

    for three_tasks in chunked(range(0, len(coroutines)), 3):
        extracted_phones = await asyncio.gather(*coroutines[three_tasks[0]:three_tasks[-1]+1])
        time.sleep(1)

        all_users = []
        [all_users.extend(execute.get('response')) for execute in extracted_phones]

        for user in all_users:
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
                    json_result.update({id_user: finish_print})

            pbar.update(1)
            offset += 25000

    with open("data_base.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(json_result, indent=4, ensure_ascii=False))

    pbar.close()
    print()

    with open("data_base.json", "r", encoding="utf-8") as file:
        json_result = json.load(file)
        return json_result, True


async def search(params):
    # LIMIT REQUEST 3 in 1 sec
    url = "https://api.vk.com/method/execute?"

    session = aiohttp.ClientSession()
    response = await session.post(url=url, data=params)
    execute_data = await response.json()
    await session.close()

    return execute_data
