import os
import re
from pathlib import Path
from urllib.parse import urlparse
import toolbox
from bs4 import BeautifulSoup
import pandas as pd

folder_path_active_ico = str(Path("Data", "Active ICO"))
folder_path_ended_ico = str(Path("Data", "Ended ICO"))
folder_path_upcoming_ico = str(Path("Data", "Upcoming ICO"))

folder_path_active_ico_new = str(Path("New_Data", "Active ICO"))
folder_path_ended_ico_new = str(Path("New_Data", "Ended ICO"))
folder_path_upcoming_ico_new = str(Path("New_Data", "Upcoming ICO"))

regex_social_lik = re.compile(r"\.\w+$")
folders = [
    folder_path_active_ico,
    folder_path_ended_ico,
    folder_path_upcoming_ico,

    folder_path_active_ico_new,
    folder_path_ended_ico_new,
    folder_path_upcoming_ico_new,
]
social_media_index = dict()
count_social_link = 1


def get_html_files(folder_path):
    # Ищет все файлы .html в определенной папке.
    html_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".html"):
                html_files.append(os.path.join(root, file))
    return html_files


def get_social_media_names(links_wb: list, data_dict: dict):
    # if data_dict['name'] == 'Wall Street Memes':
    #     print(f"{links_wb=}\n{data_dict['name']=}")
    #     print('--' * 40)
    global count_social_link
    global social_media_index

    for social_link in links_wb:
        parsed_url = urlparse(social_link)
        website_name = parsed_url.netloc.replace('www.', '')
        social_name = re.sub(regex_social_lik, '', website_name)
        if social_name == 't':
            social_name = 't.me'

        if social_name not in social_media_index.keys():
            social_media_index[social_name] = count_social_link
            count_social_link += 1

        data_dict[f"{social_media_index[social_name]}_{social_name}"] = social_link

    # if data_dict['name'] == 'Wall Street Memes':
    #     for k, v in data_dict.items():
    #         print(f"{k}: {v}")
    #     print('==' * 40)
    return data_dict


def get_important(soup, data_dict: dict):
    data_dict['important_text_1'] = None
    data_dict['important_link_1'] = None

    important_tag = soup.find("div", {"class": "important-note"})
    try:
        important = re.sub(r"Details", "", str(important_tag)).replace('Important:', '').strip()
    except:
        return data_dict

    important_tags = important.split('<br/>')
    for t, tags_text_i in enumerate(important_tags, start=1):
        if len(tags_text_i) < 7:
            continue
        # print(tags_text_i)
        try:
            soup2 = BeautifulSoup(tags_text_i, "lxml")
        except Exception as err_soup:
            print(f"{err_soup=}")

        important_text = soup2.text.replace(' ().', '').strip()
        important_link = soup2.find('a')
        if important_link:
            important_link = important_link.get('href')

        data_dict[f'important_text_{t}'] = important_text
        data_dict[f'important_link_{t}'] = important_link

    return data_dict


def get_token_sale(right_column, dict_data_text_cards):
    con_sale = ''
    try:
        token_sale_tag = right_column.find("div", {"class": "token-sale"})
        if token_sale_tag:
            token_sale_strong = token_sale_tag.find("strong")
            if token_sale_strong:
                token_sale = token_sale_strong.text.replace('\n', '')
                if token_sale != '':
                    # print(f"{token_sale=}")
                    con_sale += token_sale.replace('ended', 'ended ')

                if not token_sale_tag.find("div"):
                    sale_date1 = right_column.find("div", class_="sale-date")
                    if sale_date1:
                        con_sale += ' ' + sale_date1.text
                    sale_date2 = right_column.find("div", {"class": "sale-date active"})
                    if sale_date2 and sale_date2 != sale_date1:
                        if sale_date2:
                            con_sale += ' ' + sale_date2.text
    except Exception as err:
        print(f"{err}\n !!! ERROR")

    dict_data_text_cards['token_sale'] = con_sale
    return dict_data_text_cards


def sort_dicts_by_max_keys(list_of_dicts):
    set_keys = set()
    if not list_of_dicts:
        return []
    # Собираем все ключи словарей:
    for data_dict in list_of_dicts:
        for key in data_dict:
            set_keys.add(key)
    # max_dict = max(list_of_dicts, key=len)
    # Отсортировать ключи эталонного словаря
    # sorted_keys = sorted(max_dict.keys())
    sorted_keys = sorted(list(set_keys))
    # Создать новые словари с отсортированными ключами
    sorted_dicts = [
        {key: dct.get(key, None) for key in sorted_keys}
        for dct in list_of_dicts
    ]
    # Отсортировать список новых словарей
    # sorted_list = sorted(sorted_dicts, key=lambda x: [x[key] if x[key] is not None else "" for key in sorted_keys])
    return sorted_dicts


def pars_txt_data(logger=None):

    for path_html_file_folder in folders:
        total_data_list = []
        name_category = os.path.split(path_html_file_folder)[-1].replace(' ', '_')
        path_files_html = get_html_files(path_html_file_folder)
        count_cards = len(path_files_html)
        print(f"{count_cards=}\n")
        if logger:
            logger.info(f"Парсинг категории: {name_category}. Всего карточек: {count_cards}")

        
        for file_ in path_files_html:
            html_data = toolbox.download_txt_data(path_file=file_)
            soup = BeautifulSoup(html_data, "lxml")

            dict_data_text_cards = {
                "1_apath_dir": str(file_),
                "name": None,
                "type_": None,
                "about": None,
                "token_sale": None,
                "received": None,

                "youtube_video_link": None,
                "website": None,
                "whitepaper": None,

                "token_sale_date": None,
                "ticker": None,
                "token_type": None,
                "ico_token_price": None,
                "fundraising_goal": None,
                "total_tokens": None,
                "available_for_token_sale": None,
                "min_max_personal_cap": None,
                "accepts": None,
                "role_of_token": None,

                "Hype rate": None,
                "Risk rate": None,
                "ROI rate": None,
                "ICO Drops Score": None,
            }

            dict_data_text_cards = get_important(soup, dict_data_text_cards)

            name = soup.find("div", {"class": "ico-main-info"}).find("h3").text.strip()
            dict_data_text_cards['name'] = name

            type_ = soup.find("span", {"class": "ico-category-name"}).text
            type_ = re.search(r"\(.+\)", type_)
            if type_:
                type_ = type_.group()
            dict_data_text_cards['type_'] = type_

            about = soup.find("div", {"class": "ico-description"})
            if about:
                about = about.text.strip()
            dict_data_text_cards['about'] = about

            # =====================================================================================================
            right_column = soup.find("div", {"class", "ico-right-col"})
            dict_data_text_cards = get_token_sale(right_column, dict_data_text_cards)

            received = soup.find("div", {"class": "fund-goal"}).text
            received = received.replace('\n', ' ').strip()
            dict_data_text_cards['received'] = received

            website = soup.find("div", {"class": "ico-right-col"}).find("div", string="WEBSITE")
            try:
                website = website.parent.get('href')
            except AttributeError:
                # print("3.0: ", file_)
                pass
            dict_data_text_cards['website'] = website

            whitepaper = soup.find("div", {"class": "ico-right-col"}).find("div", string="WHITEPAPER")
            try:
                whitepaper = whitepaper.parent.get('href')
            except AttributeError:
                # print("3.1: ", file_)
                pass
            dict_data_text_cards['whitepaper'] = whitepaper

            social_links = [link.get("href") for link in soup.find("div", {"class": "soc_links"}).find_all("a")]

            token_sale_date = soup.find("div", {"class": "col-12 title-h4"}).find("h4").text
            token_sale_date = token_sale_date.replace("Token Sale:", "").replace("\n", "").strip()
            if token_sale_date == 'Market & Returns':
                token_sale_date = None
            dict_data_text_cards['token_sale_date'] = token_sale_date

            ticker_tag = soup.find("span", string="Ticker: ")
            if ticker_tag:
                ticker = ticker_tag.next_sibling.text.strip()
            else:
                ticker = None
            dict_data_text_cards['ticker'] = ticker

            token_type_tag = soup.find("span", string="Token type: ")
            if token_type_tag:
                token_type = token_type_tag.next_sibling.text.strip()
            else:
                token_type = None
            dict_data_text_cards['token_type'] = token_type

            ico_token_price_tag = soup.find("span", string="ICO Token Price:")
            if ico_token_price_tag:
                ico_token_price = ico_token_price_tag.next_sibling.text.strip()
            else:
                ico_token_price = None
            dict_data_text_cards['ico_token_price'] = ico_token_price

            youtube_video_link = soup.find("iframe", {"allow": True})
            # print(f"{youtube_video_link=}")
            if youtube_video_link:
                youtube_video_link = youtube_video_link.get("src")
            dict_data_text_cards['youtube_video_link'] = youtube_video_link

            fundraising_goal_tag = soup.find("div", {"class": "fund-goal"}).find("div", {"class": "goal"})
            if fundraising_goal_tag:
                fundraising_goal = fundraising_goal_tag.text.strip()
                fundraising_goal = re.search(r"\$.+(?=[ (])", fundraising_goal)
                if fundraising_goal:
                    fundraising_goal = fundraising_goal.group()
            else:
                fundraising_goal = None
            dict_data_text_cards['fundraising_goal'] = fundraising_goal

            total_tokens_tag = soup.find("span", string="Total Tokens: ")
            if total_tokens_tag:
                total_tokens = total_tokens_tag.next_sibling.text.strip()
            else:
                total_tokens = None
            dict_data_text_cards['total_tokens'] = total_tokens

            available_for_token_sale_tag = soup.find("span", string="Available for Token Sale: ")
            if available_for_token_sale_tag:
                available_for_token_sale = available_for_token_sale_tag.next_sibling.text.strip()
            else:
                available_for_token_sale = None
            dict_data_text_cards['available_for_token_sale'] = available_for_token_sale

            min_max_personal_cap_tag = soup.find("span", string="Min/Max Personal Cap: ")
            if min_max_personal_cap_tag:
                min_max_personal_cap = min_max_personal_cap_tag.next_sibling.text.strip()
            else:
                min_max_personal_cap = None
            dict_data_text_cards['min_max_personal_cap'] = min_max_personal_cap

            accepts_tag = soup.find("span", string="Accepts: ")
            if accepts_tag:
                accepts = accepts_tag.next_sibling.text.strip()
            else:
                accepts = None
            dict_data_text_cards['accepts'] = accepts

            role_of_token_tag = soup.find("span", string="Role of Token: ")
            if role_of_token_tag:
                role_of_token = role_of_token_tag.next_sibling.text.strip()
            else:
                role_of_token = None
            dict_data_text_cards['role_of_token'] = role_of_token

            try:
                additional_links = [link_add.get('href') for link_add in soup.find(
                    "div", {"class": "row list-thin"}).find_all('a')]
                additional_links_name = [link_add.text.strip() for link_add in soup.find(
                    "div", {"class": "row list-thin"}).find_all('a')]

                count_links = 1
                for link, name_lick in zip(additional_links, additional_links_name):
                    dict_data_text_cards[f'additional_link{count_links}'] = link
                    dict_data_text_cards[f'additional_name{count_links}'] = name_lick
                    count_links += 1
            except AttributeError:
                pass
                # print("4: ", file_)

            dur_rating_block = soup.find("div", {"class": "ico-row rating-field"})
            if dur_rating_block:
                rating_boxs = soup.find_all("div", {"class": "rating-box"})
                # print('\n')
                for rating_box in rating_boxs:
                    key_rating = rating_box.find("p", {"class": None})
                    if key_rating:
                        key_rating = key_rating.text.strip()
                        if key_rating == "ICO Drps score":
                            key_rating = "ICO Drops Score"
                        dict_data_text_cards[key_rating] = rating_box.find("p", {"class": True}).text.strip()
                    # print(rating_box.text)
                    # print('--' * 40)

            # print(
            #     f"Important: {important}\n\nName: {name}\n\nType: {type_}\n\n"
            #     f"Token Sale: {token_sale}\n\nReceived: {received}\n\nWebsite: {website}\n\n"
            #     f"Social Links: {social_links} {len(social_links)=}\n\nToken sale date: {token_sale_date}\n\n"
            #     f"Ticker: {ticker}\n\nToken type: {token_type}\n\nICO Token Price: {ico_token_price}\n\n"
            #     f"Fundraising Goal: {fundraising_goal}\n\nTotal Tokens: {total_tokens}\n\n"
            #     f"Available for Token Sale: {available_for_token_sale}\n\n"
            #     f"Min/Max Personal Cap: {min_max_personal_cap}\n\nAccepts: {accepts}\n\n"
            #     f"Role of Token: {role_of_token}\n\n"
            #     f"ADDITIONAL LINKS: {additional_links}"
            # )

            data_df = get_social_media_names(social_links, dict_data_text_cards)
            total_data_list.append(data_df)
            # print('==' * 40)

        total_data_list = sort_dicts_by_max_keys(list_of_dicts=total_data_list)
        df = pd.DataFrame(total_data_list)
        path_res_xlsx = str(Path(path_html_file_folder, f"Txt_Data_Cards_{name_category}.csv"))
        try:
            df.to_csv(path_res_xlsx, index=False)
        except OSError as os_err:
            print(os_err)
            pass


if __name__ == '__main__':
    pars_txt_data()
