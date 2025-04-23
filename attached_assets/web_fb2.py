import tkinter as tk
from tkinter import filedialog
import os
import nltk
nltk.download('punkt')

# Создаем графический интерфейс
app = tk.Tk()
app.title("Конвертер в FB2")
app.geometry("300x100")

# Функция для выбора файла и открытия в FB2
def select_file_and_open_fb2():
    file_path = filedialog.askopenfilename(title="Выберите текстовый файл", filetypes=[("Text Files", "*.txt")])
    if file_path:
        # Анализируем текстовый файл
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            lines = process_text(text)

        # Получаем имя файла без расширения
        file_name = os.path.splitext(os.path.basename(file_path))[0]

        # Формируем имя выходного файла
        output_file_name = f"{file_name}_formatted.fb2"

        # Сохраняем результат в FB2
        with open(output_file_name, 'w', encoding='utf-8') as file:
            file.write('\n'.join(lines))

        # Открываем файл в браузере с использованием кавычек в пути
        output_file_url = f'file:///{os.path.normpath(os.path.abspath(output_file_name)).replace(os.sep, "/")}'
        os.system(f'start "" "{output_file_url}"')

# создаем кнопку "Открыть в FB2"
open_fb2_button = tk.Button(app, text="Открыть в FB2", command=select_file_and_open_fb2)
open_fb2_button.pack(pady=10)

# Функция для токенизации текста
def process_text(input_text):
    tokens = nltk.word_tokenize(input_text)
    lines = []

    current_line = []
    for token in tokens:
        current_line.append(token)
        if len(current_line) >= 25:
            lines.append(' '.join(current_line))
            current_line = []

    if current_line:
        lines.append(' '.join(current_line))

    return lines

# Запускаем главный цикл событий
app.mainloop()
