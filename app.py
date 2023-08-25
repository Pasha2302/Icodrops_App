import signal
import subprocess
import time
import threading
import zipfile
import shutil

from flask import (
    Flask, request, g, session,
    url_for, current_app, flash,
    render_template, redirect, jsonify, Response, send_file
)

import sys
import os
from pathlib import Path
import toolbox


pid = os.getpid()
toolbox.save_txt_data(data_txt=str(pid), path_file='process_id.txt')
absolute_path_to_interpreter = sys.executable

process = False
file_path = str(Path('New_Data'))

check_download_data = {'finish': False, 'down': False}
if os.path.isfile("check_download_data.json"):
    check_download_data = toolbox.download_json_data(path_file="check_download_data.json")


start_date = toolbox.date_str(time.time())
if os.path.isfile("start_date.txt"):
    start_date = toolbox.download_txt_data(path_file='start_date.txt').strip()
script_state = "Не запущен"
if os.path.isfile('script_state.txt'):
    script_state = toolbox.download_txt_data(path_file="script_state.txt").strip()

app = Flask(__name__)
app.config.from_object(__name__)


# Загружаем конфиг по умолчанию и переопределяем в конфигурации часть
# значений через переменную окружения
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=False,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


with app.app_context():
    print(f"Текущее приложение: {current_app.name}")


menu = [
    {'name': 'Главная', 'url': '/'},
    {'name': 'Контакты', 'url': '/contact'},
]

button_state = 0
if os.path.isfile("button_state.txt"):
    button_state = toolbox.download_txt_data(path_file='button_state.txt')


@app.route('/sss')
def test_sss():
    print("\n test_sss() >>>")
    return render_template('password.html')


@app.route('/stop', methods=['POST'])
def stop():
    password = request.form.get('password')
    if password == '6021023':  # Замените на ваш реальный пароль
        os.kill(os.getpid(), signal.SIGINT)
        return "<h1> Flask KiLL...</h1>"
    else:
        return "<h1>Неверный пароль</h1>"
# -----------------------------------------------------------------------------------------------------------------


def remove_folder(folder_path):
    try:
        shutil.rmtree(folder_path)
        print(f"Папка '{folder_path}' успешно удалена")
    except Exception as e:
        print(f"Ошибка при удалении папки '{folder_path}': {e}")


def script_state_generator():
    while True:
        yield f"data: {script_state}\n\n"
        time.sleep(4)


@app.route('/stream')
def stream():
    return Response(script_state_generator(), mimetype='text/event-stream')


@app.route('/index.html')
@app.route('/')
def index():
    return render_template('index.html', menu=menu, script_state=script_state)


@app.route('/contact')
def contact():
    return render_template('contact.html', menu=menu)


def read_last_non_empty_line(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in reversed(lines):
            if line.strip():  # Проверка на пустую строку
                return line.strip()


def zip_folder(folder_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)


def generate_script_output():
    global process
    global script_state
    global button_state
    global start_date
    script_state = "Скрипт запущен (идет процесс сбора данных)"

    print("generate_script_output")
    try:
        process = subprocess.Popen([absolute_path_to_interpreter, 'main.py'],
                                   stdout=subprocess.PIPE, universal_newlines=True)
    except Exception as error_process:
        script_state = "\nerror_process: " + str(error_process)

    while True:
        time.sleep(5)  # Добавьте небольшую задержку, чтобы не перегружать сервер
        output = read_last_non_empty_line('main.log')
        if process.poll() is not None:
            break
        if output:
            print(output)
            script_state = output

    start_date = toolbox.date_str(time.time())
    if process.poll() == 0:
        script_state = "Скрипт завершил работу (нужно забрат файл с данными!)..."
        check_download_data['finish'] = True
        toolbox.save_json_data(json_data=check_download_data, path_file="check_download_data.json")
        print(f'\nFinish Process: {process.poll()=}')


@app.route('/download', methods=['POST'])
def download():
    global button_state
    global check_download_data
    global script_state
    out_path_zip = 'New_Data.zip'
    # check_download_data['finish'] = True

    if os.path.exists(file_path) and check_download_data['finish']:
        # Устанавливаем имя файла, как его имя, извлеченное из пути
        filename = out_path_zip.split('/')[-1]
        try:
            if not os.path.isfile(out_path_zip):
                script_state = f"Подождите, идет архивация данных! (Это может занять некоторое время...)"
                zip_folder(folder_path=file_path, output_path=out_path_zip)
            res_file = send_file(out_path_zip, as_attachment=True, download_name=filename)
            if res_file:
                check_download_data['down'] = True
                script_state = f"Не запущен (Данные получены. Последний запуск был: {start_date})"
                return res_file
            else:
                script_state = f"Данные не Получены!!!"
        except Exception as err_down:
            print(err_down)
            check_download_data['down'] = False

    else:
        script_state = f"Сбор данных не завершен, завершите сбор данных! (Последний запуск был: {start_date})"
    button_state = 0
    return redirect(url_for('index'))


@app.route('/buttons', methods=['POST'])
def buttons():
    global script_state
    global button_state
    global process
    global check_download_data
    global start_date

    button_value = request.form.get('button_value')
    print(f'Пользователь нажал на кнопку с значением: {button_value}\n{button_state=}')

    if button_state == 0 and button_value == 'button1':
        if check_download_data['finish'] and check_download_data['down']:
            if os.path.exists(file_path):
                remove_folder(folder_path=file_path)
            if os.path.isfile(f"{file_path}.zip"):
                os.remove(f"{file_path}.zip")

        check_download_data = {'finish': False, 'down': False}
        print("Запуск script_tt.py")
        start_date = toolbox.date_str(time.time())
        threading.Thread(target=generate_script_output).start()
        button_state = 1

    elif button_value == 'button2' and button_state == 1:
        # flash("Скрипт остановлен", category='error')
        print(f"{process.poll()=}")
        while process.poll() is None:
            process.terminate()
            time.sleep(1.5)
        script_state = "Скрипт остановлен (Возможно не все данные были собраны, запустите повторно...)"
        print(f"{process.poll()=} {type(process.poll())}")
        if not check_download_data['finish']:
            button_state = 0

    return redirect(url_for('index'))


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=None)
        print('Off')
    except KeyboardInterrupt as err:
        print(err)
    finally:
        toolbox.save_txt_data(start_date, path_file='start_date.txt')
        toolbox.save_txt_data(str(button_state), path_file='button_state.txt')
        toolbox.save_txt_data(script_state, path_file='script_state.txt')
        toolbox.save_json_data(json_data=check_download_data, path_file="check_download_data.json")
        sys.exit()
