import re
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tqdm import tqdm
import os

# Функция для чтения списка цветов из файла
def read_colors_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        colors = [line.strip() for line in f]
    return colors

# Функция для поиска предложений с цветами в тексте
def find_sentences_with_colors(text, colors):
    sentences = text.split('.')
    sentences_with_colors = []
    for sentence in tqdm(sentences, desc='Поиск'):
        for color in colors:
            if re.search(r'\b{}\b'.format(color), sentence, re.IGNORECASE):
                sentence_words = sentence.strip().split()
                formatted_sentence = ""
                word_count = 0
                for word in sentence_words:
                    if word_count + len(word.split('\n')) <= 20:
                        formatted_sentence += word + " "
                        word_count += len(word.split('\n'))
                    else:
                        sentences_with_colors.append(formatted_sentence.strip() + '.')
                        formatted_sentence = word + " "
                        word_count = len(word.split('\n'))
                if formatted_sentence.strip():
                    sentences_with_colors.append(formatted_sentence.strip() + '.')
                break
    return sentences_with_colors

# Функция для запуска анализа
def analyze():
    colors_filename = colors_file_entry.get()
    colors = read_colors_from_file(colors_filename)
    
    text_filename = text_file_entry.get()
    with open(text_filename, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Extracting file names without extensions
    text_filename_without_ext = os.path.splitext(os.path.basename(text_filename))[0]
    colors_filename_without_ext = os.path.splitext(os.path.basename(colors_filename))[0]
    
    # Constructing the output file name
    output_file_name = f"{text_filename_without_ext}_{colors_filename_without_ext}.txt"
    
    with open(output_file_name, 'w', encoding='utf-8') as f:
        sentences_with_colors = find_sentences_with_colors(text, colors)
        for sentence in tqdm(sentences_with_colors, desc='Запись в файл'):
            f.write(sentence + '\n')
        result_label.config(text="Анализ завершен!")

# Создание GUI
root = tk.Tk()
root.title("Анализатор текста")

# Фрейм для выбора файла с цветами
colors_frame = ttk.Frame(root)
colors_frame.pack(pady=10)
colors_label = ttk.Label(colors_frame, text="Список слов:")
colors_label.grid(row=0, column=0, padx=5)
colors_file_entry = ttk.Entry(colors_frame, width=50)
colors_file_entry.grid(row=0, column=1, padx=5)
colors_file_button = ttk.Button(colors_frame, text="Выбрать файл", command=lambda: colors_file_entry.insert(tk.END, filedialog.askopenfilename()))
colors_file_button.grid(row=0, column=2, padx=5)

# Фрейм для выбора файла с текстом
text_frame = ttk.Frame(root)
text_frame.pack(pady=10)
text_label = ttk.Label(text_frame, text="Файл анализа:")
text_label.grid(row=0, column=0, padx=5)
text_file_entry = ttk.Entry(text_frame, width=50)
text_file_entry.grid(row=0, column=1, padx=5)
text_file_button = ttk.Button(text_frame, text="Выбрать файл", command=lambda: text_file_entry.insert(tk.END, filedialog.askopenfilename()))
text_file_button.grid(row=0, column=2, padx=5)

# Кнопка запуска анализа
analyze_button = ttk.Button(root, text="Запустить анализ", command=analyze)
analyze_button.pack(pady=10)

# Метка для вывода результата
result_label = ttk.Label(root, text="")
result_label.pack(pady=5)

root.mainloop()
