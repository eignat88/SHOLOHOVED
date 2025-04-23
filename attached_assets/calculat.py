def calculate_reading_time(text, words_per_minute=200):
    # Разбиваем текст на слова
    words = text.split()
    # Подсчитываем количество слов в тексте
    num_words = len(words)
    # Рассчитываем время чтения в минутах
    reading_time_minutes = num_words / words_per_minute
    # Преобразуем время в формат минут и секунд
    minutes = int(reading_time_minutes)
    seconds = int((reading_time_minutes - minutes) * 60)
    return minutes, seconds

def read_text_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

# Указываем путь к файлу
file_path = r"D:\SHOLOHOVED\SHOLOHOVED\как_Аксинья.txt"

# Читаем текст из файла
text = read_text_from_file(file_path)

# Рассчитываем время чтения
minutes, seconds = calculate_reading_time(text)

print(f"Время чтения: {minutes} минут и {seconds} секунд")
