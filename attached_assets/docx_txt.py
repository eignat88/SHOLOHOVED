import tkinter as tk
from tkinter import filedialog
import os
import docx2txt

# Создаем графический интерфейс
app = tk.Tk()
app.title("Конвертер в TXT")
app.geometry("300x100")

# Функция для выбора файла и открытия в TXT
def select_file_and_open_txt():
    file_path = filedialog.askopenfilename(title="Выберите файл DOCX", filetypes=[("Word Files", "*.docx")])
    if file_path:
        # Проверяем, является ли выбранный файл действительным файлом DOCX
        if file_path.lower().endswith('.docx'):
            # Конвертируем DOCX в текст
            text = docx2txt.process(file_path)

            # Получаем имя файла без расширения
            file_name = os.path.splitext(os.path.basename(file_path))[0]

            # Формируем имя выходного файла
            output_file_name = f"{file_name}.txt"

            # Сохраняем результат в TXT
            with open(output_file_name, 'w', encoding='utf-8') as file:
                file.write(text)

            # Открываем файл в блокноте
            os.system(f'notepad.exe "{output_file_name}"')
        else:
            tk.messagebox.showerror("Ошибка", "Выбранный файл не является файлом DOCX")

# Создаем кнопку "Открыть в TXT"
open_txt_button = tk.Button(app, text="Открыть в TXT", command=select_file_and_open_txt)
open_txt_button.pack(pady=10)

# Запускаем главный цикл событий
app.mainloop()
