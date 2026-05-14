import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
import threading
from tqdm import tqdm
from modules.platform_open import open_file

class WordSearchFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.last_found_words = []
        self.create_widgets()

    def create_widgets(self):
        file_frame = ttk.LabelFrame(self, text="Выбор файла")
        file_frame.pack(fill="x", padx=10, pady=10, expand=False)

        self.file_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_var, width=60)
        self.file_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.browse_button = ttk.Button(file_frame, text="Обзор", command=self.browse_file)
        self.browse_button.grid(row=0, column=1, padx=5, pady=5)

        search_frame = ttk.LabelFrame(self, text="Поиск")
        search_frame.pack(fill="x", padx=10, pady=10, expand=False)

        ttk.Label(search_frame, text="Введите слово или его часть для поиска:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        self.search_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.search_button = ttk.Button(search_frame, text="Найти", command=self.start_search)
        self.search_button.grid(row=1, column=1, padx=5, pady=5)

        self.clear_button = ttk.Button(search_frame, text="Сброс", command=self.clear_search)
        self.clear_button.grid(row=1, column=2, padx=5, pady=5)

        result_frame = ttk.LabelFrame(self, text="Результаты поиска")
        result_frame.pack(fill="both", padx=10, pady=10, expand=True)

        self.result_text = tk.Text(result_frame, wrap="word", height=10)
        self.result_text.pack(fill="both", expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(self.result_text, command=self.result_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.result_text.config(yscrollcommand=scrollbar.set)

        self.copy_button = ttk.Button(result_frame, text="Копировать результаты", command=self.copy_results)
        self.copy_button.pack(pady=5)

        self.save_button = ttk.Button(
            result_frame, text="Сохранить результаты", command=self.save_results, state="disabled"
        )
        self.save_button.pack(pady=5)

        file_frame.columnconfigure(0, weight=1)
        search_frame.columnconfigure(0, weight=1)

    def browse_file(self):
        filetypes = [("Text files", "*.txt")]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.file_var.set(filename)

    def start_search(self):
        file_path = self.file_var.get()
        search_word = self.search_var.get().lower()

        if not file_path:
            messagebox.showerror("Ошибка", "Выберите файл для поиска!")
            return
        if not search_word:
            messagebox.showerror("Ошибка", "Введите слово для поиска!")
            return
        if not os.path.exists(file_path):
            messagebox.showerror("Ошибка", "Указанный файл не существует!")
            return

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Выполняется поиск...\n")
        self.save_button.config(state="disabled")
        self.last_found_words = []

        search_thread = threading.Thread(target=self.perform_search, args=(file_path, search_word))
        search_thread.daemon = True
        search_thread.start()

    def perform_search(self, file_path, search_word):
        try:
            found_words = []

            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    for word in line.split():
                        if search_word in word.lower():
                            found_words.append(word)

            found_words = sorted(set(found_words))
            self.after(0, lambda: self.display_search_results(found_words))

        except Exception as e:
            error_message = f"Ошибка при поиске: {str(e)}"
            self.after(0, lambda: self.display_search_error(error_message))

    def display_search_error(self, error_message):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, error_message)
        self.save_button.config(state="disabled")

    def display_search_results(self, found_words):
        self.result_text.delete(1.0, tk.END)
        self.last_found_words = found_words

        if found_words:
            formatted_results = self.format_results(found_words)
            self.result_text.insert(tk.END, f"Найденные слова:\n{formatted_results}")
            self.save_button.config(state="normal")
        else:
            self.result_text.insert(tk.END, "Слово не найдено.")
            self.save_button.config(state="disabled")

    def format_results(self, words):
        return "\n".join(words)

    def clear_search(self):
        self.search_var.set("")
        self.result_text.delete(1.0, tk.END)
        self.last_found_words = []
        self.save_button.config(state="disabled")

    def copy_results(self):
        result_text = self.result_text.get(1.0, tk.END)
        self.clipboard_clear()
        self.clipboard_append(result_text)
        messagebox.showinfo("Копирование", "Результаты скопированы в буфер обмена")

    def save_results(self):
        if not self.last_found_words:
            messagebox.showinfo("Сохранение", "Нет результатов для сохранения.")
            return

        source_path = self.file_var.get()
        if not source_path or not os.path.exists(source_path):
            messagebox.showerror("Ошибка", "Исходный файл не найден.")
            return

        out_dir = os.path.dirname(source_path)
        first_word = self.last_found_words[0]

        safe_name = re.sub(r'[<>:"/\\|?*\n\r\t]', "_", first_word).strip()
        if not safe_name:
            safe_name = "results"

        out_path = os.path.join(out_dir, f"{safe_name}.txt")

        # чтобы не перезатирать — добавим суффикс _2, _3...
        base, ext = os.path.splitext(out_path)
        i = 2
        while os.path.exists(out_path):
            out_path = f"{base}_{i}{ext}"
            i += 1

        try:
            with open(out_path, "w", encoding="utf-8") as f:
                for w in self.last_found_words:
                    f.write(w + "\n")
            messagebox.showinfo("Сохранение", f"Результаты сохранены:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")


class ColorAnalysisFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Создаем элементы интерфейса анализа цветов
        self.create_widgets()
    
    def create_widgets(self):
        # Фрейм для выбора файла списка цветов
        colors_frame = ttk.LabelFrame(self, text="Список слов")
        colors_frame.pack(fill="x", padx=10, pady=10, expand=False)
        
        ttk.Label(colors_frame, text="Файл со списком слов:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.colors_file_var = tk.StringVar()
        self.colors_file_entry = ttk.Entry(colors_frame, textvariable=self.colors_file_var, width=50)
        self.colors_file_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.colors_file_button = ttk.Button(
            colors_frame, text="Обзор", 
            command=lambda: self.browse_file(self.colors_file_var)
        )
        self.colors_file_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Фрейм для выбора текстового файла для анализа
        text_frame = ttk.LabelFrame(self, text="Файл для анализа")
        text_frame.pack(fill="x", padx=10, pady=10, expand=False)
        
        ttk.Label(text_frame, text="Текстовый файл:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.text_file_var = tk.StringVar()
        self.text_file_entry = ttk.Entry(text_frame, textvariable=self.text_file_var, width=50)
        self.text_file_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.text_file_button = ttk.Button(
            text_frame, text="Обзор", 
            command=lambda: self.browse_file(self.text_file_var)
        )
        self.text_file_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Кнопка запуска анализа
        self.analyze_button = ttk.Button(
            self, text="Запустить анализ", 
            command=self.start_analysis
        )
        self.analyze_button.pack(pady=10)
        
        # Индикатор прогресса
        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="indeterminate")
        self.progress.pack(pady=5, fill="x", padx=10)
        
        # Текстовое поле для вывода статуса операции
        self.status_text = tk.Text(self, height=10, width=70, wrap="word")
        self.status_text.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Настройка scrollbar для текстового поля
        scrollbar = ttk.Scrollbar(self.status_text, command=self.status_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.status_text.config(yscrollcommand=scrollbar.set)
        
        # Делаем колонки растягиваемыми
        colors_frame.columnconfigure(1, weight=1)
        text_frame.columnconfigure(1, weight=1)
    
    def browse_file(self, var):
        """Открывает диалог выбора файла и устанавливает значение в переменную"""
        filetypes = [("Text files", "*.txt")]
        
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            var.set(filename)
    
    def start_analysis(self):
        """Запускает анализ текста в отдельном потоке"""
        colors_filename = self.colors_file_var.get()
        text_filename = self.text_file_var.get()
        
        if not colors_filename:
            messagebox.showerror("Ошибка", "Выберите файл со списком слов!")
            return
        
        if not text_filename:
            messagebox.showerror("Ошибка", "Выберите файл для анализа!")
            return
        
        # Проверяем существование файлов
        if not os.path.exists(colors_filename):
            messagebox.showerror("Ошибка", "Указанный файл со списком слов не существует!")
            return
        
        if not os.path.exists(text_filename):
            messagebox.showerror("Ошибка", "Указанный файл для анализа не существует!")
            return
        
        # Очищаем поле статуса
        self.status_text.delete(1.0, tk.END)
        self.update_status("Начало анализа...")
        
        # Запускаем прогресс-бар
        self.progress.start()
        
        # Запускаем анализ в отдельном потоке
        analyze_thread = threading.Thread(
            target=self.perform_analysis,
            args=(colors_filename, text_filename)
        )
        analyze_thread.daemon = True
        analyze_thread.start()
    
    def perform_analysis(self, colors_filename, text_filename):
        """Выполняет анализ текста"""
        try:
            # Читаем список слов из файла
            self.post_status("Чтение списка слов...")
            with open(colors_filename, 'r', encoding='utf-8') as f:
                colors = [line.strip() for line in f]
            
            # Читаем текстовый файл
            self.post_status("Чтение текстового файла...")
            with open(text_filename, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Поиск предложений с указанными словами
            self.post_status("Поиск предложений со словами из списка...")
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
            
            # Extracting file names without extensions
            text_filename_without_ext = os.path.splitext(os.path.basename(text_filename))[0]
            colors_filename_without_ext = os.path.splitext(os.path.basename(colors_filename))[0]
            
            # Constructing the output file name
            output_file_name = f"{text_filename_without_ext}_{colors_filename_without_ext}.txt"
            
            # Сохраняем результаты анализа
            self.post_status("Сохранение результатов анализа...")
            with open(output_file_name, 'w', encoding='utf-8') as f:
                for sentence in tqdm(sentences_with_colors, desc='Запись в файл'):
                    f.write(sentence + '\n')
            
            # Обновляем статус в основном потоке
            self.after(0, lambda: self.analysis_completed(output_file_name))
            
        except Exception as e:
            # Обрабатываем ошибки
            error_message = f"Ошибка при анализе: {str(e)}"
            self.post_status(error_message)
            self.after(0, lambda: self.progress.stop())
    
    def analysis_completed(self, output_file):
        """Обрабатывает завершение анализа"""
        self.progress.stop()
        self.update_status(f"Анализ завершен успешно!\nРезультат сохранен в: {output_file}")
        
        if messagebox.askyesno("Анализ завершен", 
                              "Анализ завершен успешно. Открыть результаты?"):
            # Открываем файл в программе по умолчанию
            open_file(output_file)
    
    def update_status(self, message):
        """Обновляет текстовое поле статуса"""
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)  # Прокрутка вниз

    def post_status(self, message):
        """Планирует обновление статуса в главном потоке Tkinter."""
        self.after(0, lambda message=message: self.update_status(message))


class TextAnalyzerTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Создаем вложенные вкладки для разных типов анализа
        self.create_widgets()
    
    def create_widgets(self):
        # Создаем систему вложенных вкладок
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка поиска слов
        self.word_search_frame = WordSearchFrame(self.notebook)
        self.notebook.add(self.word_search_frame, text="Поиск слов")
        
        # Вкладка анализа цветов в тексте
        self.color_analysis_frame = ColorAnalysisFrame(self.notebook)
        self.notebook.add(self.color_analysis_frame, text="Анализ по списку слов")
