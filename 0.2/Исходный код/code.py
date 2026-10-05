import json ## работа с json файлами
import os ## Работа с системой
import requests ## Работа с запросами
from io import BytesIO ## Работа с кэшем
from PIL import Image ## Работа с картинками
from plyer import notification ## Работа с уведомлениями
import sys ## Работа с реестром (наверное)
import winreg ##
import time ## Время

CONFIG_FILE = "config.json"
CACHE_FILE = "cache/cache.json"
version = "0.2"


def load_json(path, default):
    if os.path.exists(path):
        try:
            return json.load(open(path, encoding="utf-8"))
        except Exception:
            return default.copy()
    return default.copy()


def save_json(path, data):
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


config = load_json(CONFIG_FILE, {})
cache = load_json(CACHE_FILE, {})

params = {
    "key": config.get("API_KEY", ""),
    "q": config.get("city", ""),
    "lang": config.get("lang", "")
}


def get_wither():
    try:
        response = requests.get(config["url"], params=params)
    except requests.exceptions.RequestException as e:
        if "--startup" not in sys.argv:
            print("\n[!] Не удалось получить погоду. Проверьте соединение, VPN или ZAPRET.")
        return False

    data = response.json()
    if config.get("debug") == "True": print(f"\n[DEBUG] Ответ сервера: {data}")
    location = data["location"]["name"]
    temperature = data["current"]["temp_c"]
    wind_speed = data["current"]["wind_kph"]
    text = data["current"]["condition"]["text"]
    icon = data["current"]["condition"]["icon"]
    feelslike = data["current"]['feelslike_c']
    humidity = data["current"]['humidity']
    chance_of_rain = data["current"]["chance_of_rain"]

    return location, temperature, wind_speed, text, icon, feelslike, humidity, chance_of_rain


def get_weather_nocification(location, temperature, wind_speed, text, icon, feelslike, humidity, chance_of_rain):
    """if icon.startswith("//"): ## Проверка на "правильную ссылку"
        icon = f"https:{icon}"
    response = requests.get(icon) ## Получение картинки
    png_img = Image.open(BytesIO(response.content)) ##Сохранение в быстрой памяти
    ICO = BytesIO()
    png_img.save(ICO, format="ICO") ## Конвертирование файла в .ico
    ICO.seek(0)"""  ##Не совсем рабочий часть кода, удалить в будущем

    if icon.startswith("//"):  ## Проверка на "правильную ссылку"
        icon = f"https:{icon}"
    response = requests.get(icon)  ## Получение картинки
    png_img = Image.open(BytesIO(response.content))  ##Сохранение в быстрой памяти

    # ИЗМЕНЕНО: Для скомпилированного .exe папка cache должна создаваться
    # рядом со сборкой, а не внутри временной системной папки распаковки PyInstaller. (идея от ИИ)
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    cache_dir = os.path.join(exe_dir, "cache")
    os.makedirs(cache_dir, exist_ok=True)
    ICO = os.path.join(cache_dir, "temp_icon.ico")

    png_img.save(ICO, format="ICO")

    notification.notify(
        title="Погода",
        message=f"Температура в {location}е: {temperature}°C.\n"
                f"Ощущается как: {feelslike}°C\n"
                f"Cкорость ветра: {wind_speed} км/ч.\n"
                f"Погода: {text}\n"
                f"Вероятность дождя: {chance_of_rain}%\n"
                f"Влажность: {humidity}%\n",
        app_name='Погода',
        app_icon=ICO,
        timeout=5
    )


#Gthtrk.xtybt Fdnjpfgecrf
def toggle_autorun():
    app_name = "WeatherWidget"

    #проверяем тип запуска
    if getattr(sys, 'frozen', False):
        #Если запущен .exe файл
        file_path = sys.executable
        cmd = f'"{file_path}" --startup'
    else:
        #Если запускается .py скрипт
        file_path = os.path.abspath(__file__)
        pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
        cmd = f'"{pythonw_path}" "{file_path}" --startup'

    #Реестр Windows
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_ALL_ACCESS
    )
    #Посмотреть включена ли автозагрузка или нет
    try:
        winreg.QueryValueEx(key, app_name)
        winreg.DeleteValue(key, app_name)
        print("\n[+] Автозагрузка программы успешно ВЫКЛЮЧЕНА!")
    except FileNotFoundError:
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, cmd)
        print("\n[+] Автозагрузка программы успешно ВКЛЮЧЕНА!")

    winreg.CloseKey(key)


def main():
    exit = False
    while exit != True:
        print("\n" + "=" * 45)
        print(f" Погодный виджет [Версия {version}]")
        print("=" * 45)
        print("1. Запустить/Выключить программу на фоне (не работает)\n"
              "2. Включить/Выключить автозагрузку программы\n"
              "3. Просмотреть статус программы (не работает)\n"
              "4. Отправить уведомление погоды\n"
              "5. Выход из консоли")
        print("=" * 45)

        user_input = input("\n[>] Выберите действие (1-5): ").strip()

        #Проверка на цифру
        if not user_input.isdigit() or not (1 <= int(user_input) <= 5):
            print('\033[H\033[J', end='')
            print("[!] Ошибка: Пожалуйста, введите корректное число от 1 до 5.")
            continue

        match int(user_input):
            case 1:
                print('\033[H\033[J', end='')
                pass
            case 2:
                print('\033[H\033[J', end='')
                toggle_autorun()
                input("\nНажмите Enter, чтобы вернуться в меню...")
                print('\033[H\033[J', end='')
            case 3:
                print('\033[H\033[J', end='')
                pass
            case 4:
                print("\n[+] Запрос данных с сервера погоды...")
                weather = get_wither()  ##location[0] temperature[1] wind_speed[2] text[3] icon[4]
                if weather != False:
                    get_weather_nocification(weather[0], weather[1], weather[2], weather[3], weather[4], weather[5],weather[6],weather[7])
                    print("[+] Уведомление успешно отправлено!")
                input("\nНажмите Enter, чтобы вернуться в меню...")
                print('\033[H\033[J', end='')
            case 5:
                print("\n[⏳] Пожалуйста, подождите. Выполняется очистка кэша...")
                try:
                    #Ищет путь (навсякий случай)
                    exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(
                        __file__)
                    cache_dir = os.path.join(exe_dir, "cache")
                    for file in os.listdir(cache_dir):
                        os.remove(os.path.join(cache_dir, file))
                    print("[+] Кэш успешно очищен.")
                except FileNotFoundError:
                    print("[!] Папка кэша не найдена, завершение работы без очистки.")

                print("[✔] Работа программы завершена. До встречи!")
                exit = True



if __name__ == "__main__":
    #Проверка автозагрузки с помощью --startup, если да то без открытия программы будет всё
    if "--startup" in sys.argv:
        wither = get_wither()
        if wither != False:
            get_weather_nocification(wither[0], wither[1], wither[2], wither[3], wither[4])

        #Очистка кэша так как запущен на фоне
        try:
            exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
            cache_dir = os.path.join(exe_dir, "cache") #Путь кэша
            for file in os.listdir(cache_dir):
                os.remove(os.path.join(cache_dir, file))
        except Exception:
            pass
        sys.exit()  #Закрываем программу потому что будет нагружать наверное
    else:
        #В случае если программу уже просто запустили
        main()
