import os
from glob import glob
import tkinter as tk
from tkinter import filedialog

def search_in_files():
    # Получаем выбранный пользователем файл
    selected_file = file_var.get()
    if not selected_file:
        result_label.config(text="Выберите файл!")
        return

    # Получаем слово для поиска
    search_word = search_entry.get().lower()

    # Создаем пустой список для хранения найденных слов
    found_words = []

    # Открываем выбранный файл для чтения
    with open(selected_file, 'r', encoding='utf-8') as file:
        # Прочитываем файл построчно
        for line in file:
            # Разделяем строку на слова
            words = line.split()
            for word in words:
                # Проверяем, содержит ли слово искомую часть
                if search_word in word.lower():
                    # Добавляем найденное слово в список
                    found_words.append(word)

    # Убираем дубликаты и сортируем список
    found_words = list(set(found_words))
    found_words.sort()

    # Выводим результат
    if found_words:
        # Форматируем список найденных слов
        formatted_results = format_results(found_words)
        result_label.config(text=f'Найденные слова: {formatted_results}')
    else:
        result_label.config(text="Слово не найдено.")

def format_results(words):
    # Форматируем список найденных слов так, чтобы не более 5 слов было в строке, каждое слово в кавычках
    formatted_results = []
    temp = []
    for word in words:
        temp.append(f'"{word}"')
        if len(temp) == 5:
            formatted_results.append(", ".join(temp))
            temp = []
    if temp:
        formatted_results.append(", ".join(temp))
    return ",\n".join(formatted_results)

def browse_files():
    # Открываем диалог выбора файла и обновляем переменную file_var
    filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    file_var.set(filename)

def clear_search():
    # Очищаем поле поиска
    search_entry.delete(0, tk.END)
    # Очищаем метку с найденными словами
    result_label.config(text="")

def copy_results():
    # Копируем текст из метки с результатами в буфер обмена
    root.clipboard_clear()
    root.clipboard_append(result_label.cget("text"))

# Создаем главное окно
root = tk.Tk()
root.title("Поиск слов в текстовых файлах")

# Создаем и настраиваем виджеты
file_label = tk.Label(root, text="Выберите файл:")
file_label.pack()

file_var = tk.StringVar()
file_entry = tk.Entry(root, textvariable=file_var, state='readonly')
file_entry.pack()

browse_button = tk.Button(root, text="Обзор", command=browse_files)
browse_button.pack()

search_label = tk.Label(root, text="Введите слово или его часть для поиска:")
search_label.pack()

search_entry = tk.Entry(root)
search_entry.pack()

search_button = tk.Button(root, text="Найти", command=search_in_files)
search_button.pack()

result_label = tk.Label(root, text="")
result_label.pack()

# Кнопка сброса
clear_button = tk.Button(root, text="Сброс", command=clear_search)
clear_button.pack()

# Кнопка копирования результатов
copy_button = tk.Button(root, text="Копировать", command=copy_results)
copy_button.pack()

# Запускаем основной цикл программы
root.mainloop()
