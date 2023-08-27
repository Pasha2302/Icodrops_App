import os
import time
from asyncio import AbstractEventLoop
import toolbox

from html_data import get_html_data
from urls_cards import start_get_cards_url
from pars_data_html import pars_txt_data
import category_check

import asyncio
import logging


if os.path.isfile('main.log'):
    os.remove('main.log')

logging.basicConfig(filename='main.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Создание объекта logger
logger = logging.getLogger(__name__)

check_data_list_url = []
if os.path.isfile('check_urls.bin'):
    check_data_list_url = toolbox.download_pickle_data('check_urls.bin').__next__()


def split_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


async def create_a_task_request(request_urls):
    data_list = []
    tasks_list = []
    exception_check = []
    path_check_card = False
    info = None

    for data_url in request_urls:
        if data_url in check_data_list_url:
            if data_url in ['https://icodrops.com/bifrost/',
                            'https://icodrops.com/cappasity/',
                            'https://icodrops.com/artoken/'
                            ]:
                info = True
                print("\nПроверка категории ранее полученной карточки")
            path_check_card = category_check.get_previous_category(source_url=data_url)
            if info:
                print(f"{data_url=}\n{path_check_card=}")

        tasks_list.append(get_html_data(session=aio_session, url=data_url, path_check=path_check_card))

    res = await asyncio.gather(*tasks_list)

    for data_validation in res:
        if not data_validation:
            exception_check.append(data_validation)
        else:
            data_list.append(data_validation)

    return data_list, exception_check


async def main():
    count_request = 0
    count_split = 25

    # ---------------------------------------------------------------------------------------------
    if not os.path.isfile('data_urls.json'):
        await start_get_cards_url(s=aio_session)
    data_urls = toolbox.download_json_data(path_file='data_urls.json')['data_urls']

    total_len = len(data_urls)
    print(f"\nTotal Len Url: {total_len}")

    for data_url in split_list(data_urls, count_split):
        res, exception_check = await create_a_task_request(request_urls=data_url)
        if exception_check:
            print('\nОшибки:')
            print(exception_check)
            return 0
        if res:
            # print('\nДанные получены')
            # print(res)
            for rr in res:
                if isinstance(rr, str):
                    if rr not in check_data_list_url:
                        check_data_list_url.append(rr)

        count_request += len(data_url)

        data_info = f"Запросов выполнено: {count_request}; Осталось: {total_len - count_request} из {total_len} запросов..."
        print(data_info)
        logger.info(data_info)
        toolbox.save_pickle_data(check_data_list_url, path_file='check_urls.bin')

    logger.info("Подождите, идет обработка текстовых данных с последующей записью в .csv")
    print("\nПодождите, идет обработка текстовых данных с последующей записью в .csv")
    try:
        pars_txt_data()
    except Exception as error_pars:
        logger.error(str(error_pars))
        raise TypeError(str(error_pars))

    if os.path.isfile('data_urls.json'):
        os.remove('data_urls.json')
    logger.info("Программа завершена...")
    print("Программа завершена...")


if __name__ == '__main__':
    try:
        pars_txt_data()
    except Exception as error_pars:
        logger.error(str(error_pars))
        raise TypeError(str(error_pars))
    
    # pip freeze > requirements.txt
    if not os.path.exists('Data'):
        os.mkdir("Data")

    if not os.path.exists('New_Data'):
        os.mkdir("New_Data")

    with toolbox.create_loop() as loop:
        loop: AbstractEventLoop

        try:
            obj_ses = toolbox.AiohttpSession(limit=15)
            aio_session = loop.run_until_complete(obj_ses.create_session())
            # loop.run_until_complete(main())
        except KeyboardInterrupt:
            pass
        except Exception as main_error:
            logger.info(str(main_error))
        finally:
            try:
                loop.run_until_complete(aio_session.close())
            except Exception as err_sess_close:
                print(err_sess_close)
            time.sleep(.35)
