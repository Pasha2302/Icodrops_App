import toolbox
import time
import os


def search_string_in_file(file_path, search_string):
    try:
        # Открываем файл на чтение
        with open(file_path, 'r') as file:
            # Читаем содержимое файла
            content = file.read()

            # Ищем строку в содержимом файла (игнорируем регистр символов)
            if search_string.lower() in content.lower():
                # return f"Адресс: [{content}] найден в: {file_path}"
                file_path_f = os.path.split(file_path)[0]
                return file_path_f
            else:
                return False

    except FileNotFoundError:
        print(f"Файл '{file_path}' не найден.")
        return False
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return False


def get_previous_category(source_url: str):
    # Ищем все txt файлы содержащие url карточки
    check_files_list_source_url = toolbox.find_files_with_extension(extension='txt', folder_path='Data')

    # Ищем в какой папке находится txt файл с искомым url карточки (в пути к файлу есть название категории карточки)
    for path_txt_file in check_files_list_source_url:
        res = search_string_in_file(file_path=path_txt_file, search_string=source_url)
        if res:
            # возвращаем путь к искомой карточке (в пути есть название категории карточки.)
            return res

    # print('\n\n', len(check_files_list_source_url))
    # print(f"Адресс: {source_url}: Не найден!...")


if __name__ == '__main__':
    data_urls = toolbox.download_json_data(path_file='data_urls.json')['data_urls']
    data_search_url = []

    for t, url in enumerate(data_urls, start=1):
        res = get_previous_category(source_url=url)
        if res:
            data_search_url.append(res)

        if t % 100 == 0:
            print('>', end='')

    print(f"\n{data_search_url=}\n{len(data_search_url)}")

    for check_cat in data_search_url:
        if 'Ended ICO' in check_cat:
            print(check_cat)
            print('--' * 40)
