import asyncio
import os
import aiohttp
import toolbox
from bs4 import BeautifulSoup
from pathlib import Path
import re
import shutil


cookies = {
    '_ym_uid': '1689587656789641065',
    '_ym_d': '1689587656',
    '_ym_isad': '2',
    '__cf_bm': '3StAzi7elfvaQYQyILliHYFfYjZ1sBRX3W0LVFUGd3I-1689587735-0-Af+/h3EQe/NThg+8+ur/VObjJ8Oq8EaixdPEXd5BCOkNlLuidWeIgt62fyNkp+lA0g==',
}

headers = {
    'authority': 'icodrops.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'no-cache',
    # 'cookie': '_ym_uid=1689587656789641065; _ym_d=1689587656; _ym_isad=2; __cf_bm=3StAzi7elfvaQYQyILliHYFfYjZ1sBRX3W0LVFUGd3I-1689587735-0-Af+/h3EQe/NThg+8+ur/VObjJ8Oq8EaixdPEXd5BCOkNlLuidWeIgt62fyNkp+lA0g==',
    'pragma': 'no-cache',
    'referer': 'https://icodrops.com/',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}

cookies2 = {
    '_ym_uid': '1690372041695849990',
    '_ym_d': '1690372041',
    '_ym_isad': '2',
    'cf_clearance': 'sqOANuH6R3_Zxs5y0EkGB9oZRGp8zRDee2peIlgLH6Y-1691692995-0-1-a80389cb.bb4c65bc.ff02d62b-0.2.1691692995',
}

headers2 = {
    'authority': 'icodrops.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',

    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    # 'cache-control': 'max-age=0',
    # 'cookie': '_ym_uid=1690372041695849990; _ym_d=1690372041; _ym_isad=2; cf_clearance=trjXrjyxF1HMh7pJ39vntg2Xf6spvtsTXTmf1f.524A-1691686114-0-1-601f6878.850d84d4.371e3798-0.2.1691686114',
    # 'if-modified-since': 'Tue, 11 Jan 2022 14:54:34 GMT',
    # 'if-none-match': '"61dd9a2a-2c7bc0"',
    'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
}

regex1 = re.compile(r"^lightbox-gallery.*")
regex2 = re.compile(r".+(?=\.)")


async def download_images(s: aiohttp.client.ClientSession, img, name_1, count_url, path_):
    img_name = img.split('/')[-1]
    img_name = re.sub(regex2, f"{name_1}_{count_url}", img_name)
    count_pay_load_error = 0
    count_err_time = 0
    count_err_disconn = 0

    while True:
        try:
            img_response = await s.get(img, cookies=cookies2, headers=headers2)
            # img_response = await s.get(img, headers=headers2)
            break
        except asyncio.exceptions.TimeoutError as err_time:
            count_err_time += 1
            await asyncio.sleep(5)
            if count_err_time == 4:
                toolbox.save_txt_data_complementing(data_txt=img, path_file='no_photo.txt')
                return 0
        except aiohttp.client.ServerDisconnectedError as err_disconn:
            count_err_disconn += 1
            await asyncio.sleep(5)
            if count_err_disconn == 4:
                raise TypeError(str(err_disconn))

    count_err_time = 0
    if img_response.status == 200:
        path_file = str(path_.joinpath(img_name.strip()))
        # Save the image to the specified path
        with open(path_file, 'wb') as f:
            while True:
                try:
                    chunk = await img_response.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)

                except aiohttp.ClientPayloadError as e:
                    print(f"\nЗапрос по: {img}")
                    print(f"Ошибка при получении ответа от сервера: {e}")
                    count_pay_load_error += 1
                    await asyncio.sleep(5)
                    if count_pay_load_error > 3:
                        raise TypeError(str(e))

                except asyncio.exceptions.TimeoutError as err_time:
                    count_err_time += 1
                    await asyncio.sleep(5)
                    if count_err_time == 4:
                        print(f"Запрос по: {img}")
                        print(f"\n\n{err_time=}")
                        toolbox.save_txt_data_complementing(data_txt=img, path_file='no_photo.txt')
                        break

        # Путь к другой директории для копирования файла
        destination_folder = path_file.replace('Data', 'New_Data', 1)
        # Скопировать файл в другую директорию
        shutil.copy(path_file, destination_folder)

        # print(f"Image '{img_name}' downloaded!")
    else:
        print("\n", "!!!!")
        print(img_response.status)
        print(img_response.headers)


async def start_download_images(session: aiohttp.client.ClientSession, html_data, path_: str, name_1):
    soup = BeautifulSoup(html_data, 'html.parser')
    image_tags = []

    image_1 = soup.find('div', {'class': 'ico-icon'}).find('img')
    # print(f"{image_1=}")
    if image_1:
        image_tags.append(image_1.get('src'))

    image_2 = soup.find("div", {"class": "img-container"})
    if image_2:
        image_2 = image_2.find("img").get('src')
        image_tags.append(image_2)
    screenshots_block = soup.find_all('a', attrs={'data-rel': regex1})
    # print(f"{screenshots_block=}")

    for screenshot in screenshots_block:
        screen1 = screenshot.get("href")
        screen2 = screenshot.get("src")
        if screen1:
            image_tags.append(screen1)
        if screen2:
            image_tags.append(screen2)

    # print()
    # print(image_tags)
    # print('==' * 40)

    tasks_list = []
    for t, url in enumerate(image_tags, start=1):
        # tasks_list.append(download_images(session, url, name_1, t, path_))
        await download_images(session, url, name_1, t, path_)

    # await asyncio.gather(*tasks_list)


async def get_html_data(session: aiohttp.client.ClientSession, url: str, path_check):
    card_search = False
    root_path = ['Data', 'New_Data']

    response = await session.get(url, cookies=cookies, headers=headers)
    if response.status == 200:
        html = await response.text()
        soup = BeautifulSoup(html, 'lxml')

        check_block = soup.find("div", {"class": "ico-breadcrumb"})
        if check_block:
            tag_info_li = check_block.find_all("li")
            if len(tag_info_li) != 3:
                print(check_block)
                raise TypeError("Неожиданные данные!!!...Проверте полученные данные!")

            # "Active ICO" , "Upcoming ICO", "Ended ICO"
            category_card = tag_info_li[-2].text.strip()

            if category_card not in ["Active ICO", "Upcoming ICO", "Ended ICO"]:
                return True

            name_card = check_block.find("li", {"class": "breadcrumb-item active"})
            if name_card:
                name_card = name_card.text.strip()

            name_card: str = name_card.replace(':', '').replace(' ', '_').replace("'", '').replace('"', '')
            name_card: str = name_card.replace('`', '')
            prefix_name = False
            list_prefix = url.split('/')
            while not prefix_name:
                prefix_name = list_prefix.pop(-1)
            name_card = f"{name_card}_{prefix_name}"
            card_search = True

        # --------------------------------------------------------------------------------------------------------
        # Проверяем, имеет ли карточка туже котегорию, что и полученая таже карточка ранее
        if path_check and category_card not in path_check:
            try:
                # Удаляем папку и ее содержимое рекурсивно
                shutil.rmtree(path_check)
                print(f"\n\n[1] Карточка '{path_check}' обновила категорию: {category_card}.")
            except FileNotFoundError:
                print(f"\n\nПапка '{path_check}' не найдена.")
            except Exception as e:
                print(f"\n\nОшибка при удалении папки: {e}")
        elif path_check and category_card in path_check:
            return True

        if card_search:
            for rp in root_path:

                path_data_html_cards_category = Path(rp, category_card)
                if not os.path.exists(path_data_html_cards_category):
                    os.mkdir(str(path_data_html_cards_category).replace("'", '').replace('"', '').replace('`', ''))

                path_directory_card = path_data_html_cards_category.joinpath(name_card)
                if not os.path.exists(path_directory_card):
                    os.mkdir(path_directory_card)

                path_html_file = str(path_directory_card.joinpath(f"{name_card}.html"))
                path_source_url = str(path_directory_card.joinpath(f"{name_card}_source_url.txt"))

            # --------------------------------------------------------------------------------------------------------

                block_html = soup.find_all("div", {"class": "col-12 col-lg-10"})[0]

                block_html = re.sub(r"<script.+</script>", '', str(block_html))
                block_html = re.sub(r"<div class=\"row justify-content-center\">[\w\W]*", '', str(block_html))

                toolbox.save_txt_data(data_txt=block_html, path_file=path_html_file)
                toolbox.save_txt_data(data_txt=url, path_file=path_source_url)
                if rp == 'Data':
                    path_directory_card_img = path_directory_card

            await start_download_images(session, block_html, path_directory_card_img, name_card)

            # print('>', end='')
            if not path_check:
                return url

        return f"{card_search=}"

    else:
        print()
        print(response.status)
        print(response.content_type)
        if response.content_type == 'text/html':
            html_error_500 = await response.text()
            toolbox.save_txt_data(data_txt=html_error_500, path_file='html_error_500.html')
        print('==' * 40)
