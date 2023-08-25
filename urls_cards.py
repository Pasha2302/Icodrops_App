import re
import toolbox
import aiohttp
from bs4 import BeautifulSoup

cookies = {
    '_ym_uid': '1690372041695849990',
    '_ym_d': '1690372041',
    '_ym_isad': '2',
    'cf_clearance': '6u0NVI3ZwB2AeeBgQ8GXCbkogwdQ3B9zpNBAl6D_5Wg-1690372284-0-0.2.1690372284',
}

headers = {
    'authority': 'icodrops.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    # 'cookie': '_ym_uid=1690372041695849990; _ym_d=1690372041; _ym_isad=2; cf_clearance=6u0NVI3ZwB2AeeBgQ8GXCbkogwdQ3B9zpNBAl6D_5Wg-1690372284-0-0.2.1690372284',
    'if-modified-since': 'Wed, 26 Jul 2023 10:53:44 GMT',
    'if-none-match': '"0b2de84a2a135cc60ee7f9b31f816550"',
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


async def get_cards_url(sess: aiohttp.client.ClientSession, url):
    correct_url = []
    print("\nЗапрос по адресу: ", url)
    response = await sess.get(url, headers=headers, cookies=cookies)

    if response.status == 200:
        print(response.content_type)
        html_data = await response.text()
        print('==' * 40)
        soup = BeautifulSoup(html_data, features="xml")
        # print(soup)

        comp = re.compile(r"\.\w+$")
        list_tag_urls = soup.find_all("loc")

        if list_tag_urls:
            for url_t in list_tag_urls:
                search_url = url_t.text
                if not re.search(comp, search_url):
                    # print(search_url)
                    correct_url.append(search_url)
                    # print('--' * 40)

            print(len(correct_url))
        else:
            print("\nБлок ссылок не найден!")

    else:
        print(response.status)
        print(response.content_type)

    return correct_url


async def start_get_cards_url(s):
    data_urls = []
    url_f = "https://icodrops.com/post-sitemap{}.xml"

    for i in range(1, 5):
        u = url_f.format(i)
        result = await get_cards_url(sess=s, url=u)
        data_urls.extend(result)

    toolbox.save_json_data(json_data={"data_urls": data_urls}, path_file='data_urls.json')
