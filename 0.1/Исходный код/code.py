import json
import os
import requests
from io import BytesIO
from PIL import Image
from plyer import notification

CONFIG_FILE = "config.json"
CACHE_FILE = "cache/cache.json"
version = "0.1"


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
    "key": config["API_KEY"],
    "q": config["city"],
    "lang": config["lang"]
}


def get_wither():
    try:
        response = requests.get(config["url"], params=params)
    except requests.exceptions.RequestException as e:
        input("\n[!] Не удалось получить погоду. Проверьте соединение, VPN или ZAPRET.\n"
              "Нажмите Enter, чтобы продолжить...")
        return False

    data = response.json()
    print(f"\n[DEBUG] Ответ сервера: {data}")
    location = data["location"]["name"]
    temperature = data["current"]["temp_c"]
    wind_speed = data["current"]["wind_kph"]
    text = data["current"]["condition"]["text"]
    icon = data["current"]["condition"]["icon"]
    return location, temperature, wind_speed, text, icon


def get_weather_nocification(location, temperature, wind_speed, text, icon):
    """if icon.startswith("//"): ## Проверка на "правильную ссылку"
        icon = f"https:{icon}"
    response = requests.get(icon) ## Получение картинки
    png_img = Image.open(BytesIO(response.content)) ##Сохранение в быстрой памяти
    ICO = BytesIO()
    png_img.save(ICO, format="ICO") ## Конвертирование файла в .ico
    ICO.seek(0)""" ##Не совсем рабочий часть кода, удалить в будущем

    if icon.startswith("//"):  ## Проверка на "правильную ссылку"
        icon = f"https:{icon}"
    response = requests.get(icon)  ## Получение картинки
    png_img = Image.open(BytesIO(response.content))  ##Сохранение в быстрой памяти

    cache_dir = os.path.join(os.path.dirname(__file__), "cache")
    os.makedirs(cache_dir, exist_ok=True)
    ICO = os.path.join(cache_dir, "temp_icon.ico")

    png_img.save(ICO, format="ICO")

    notification.notify(
        title="Погода",
        message=f"Температура в {location}е {temperature} °C.\n"
                f"Cкорость ветра {wind_speed} км/ч.\n"
                f"Погода: {text}\n",
        app_name='Погода',
        app_icon=ICO,
        timeout=5
    )


def main():
    exit = False
    while exit != True:
        print("\n" + "=" * 45)
        print(f" Погодный виджет [Версия {version}]")
        print("=" * 45)
        print("1. Запустить/Выключить программу на фоне (не работает)\n"
              "2. Включить/Выключить автозагрузку программы (не работает)\n"
              "3. Просмотреть статус программы (не работает)\n"
              "4. Отправить уведомление погоды\n"
              "5. Выход из консоли")
        print("=" * 45)

        user_input = input("\n[>] Выберите действие (1-5): ").strip()

        # Проверка на корректность ввода номера действия
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
                pass
            case 3:
                print('\033[H\033[J', end='')
                pass
            case 4:
                print("\n[+] Запрос данных с сервера погоды...")
                wither = get_wither()  ##location[0] temperature[1] wind_speed[2] text[3] icon[4]
                if wither != False:
                    get_weather_nocification(wither[0], wither[1], wither[2], wither[3], wither[4])
                    print("[+] Уведомление успешно отправлено!")
                input("\nНажмите Enter, чтобы вернуться в меню...")
                print('\033[H\033[J', end='')
            case 5:
                print("\n[⏳] Пожалуйста, подождите. Выполняется очистка кэша...")
                try:
                    for file in os.listdir("cache"):
                        os.remove(os.path.join("cache", file))
                    print("[+] Кэш успешно очищен.")
                except FileNotFoundError:
                    print("[!] Папка кэша не найдена, завершение работы без очистки.")

                print("[✔] Работа программы завершена. До встречи!")
                exit = True


if __name__ == "__main__":
    main()
