import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import re
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from wordcloud import WordCloud

class TextStatisticsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Создаем элементы интерфейса
        self.create_widgets()
    
    def create_widgets(self):
        # Создаем систему вложенных вкладок для разных типов статистики
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка частотного анализа
        self.frequency_frame = FrequencyAnalysisFrame(self.notebook)
        self.notebook.add(self.frequency_frame, text="Частотный анализ")
        
        # Вкладка облака слов
        self.wordcloud_frame = WordCloudFrame(self.notebook)
        self.notebook.add(self.wordcloud_frame, text="Облако слов")


class FrequencyAnalysisFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Создаем элементы интерфейса
        self.create_widgets()
    
    def create_widgets(self):
        # Фрейм для выбора файла
        file_frame = ttk.LabelFrame(self, text="Выбор файла")
        file_frame.pack(fill="x", padx=10, pady=10, expand=False)
        
        # Поле для отображения выбранного файла
        self.file_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_var, width=60)
        self.file_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Кнопка для выбора файла
        self.browse_button = ttk.Button(file_frame, text="Обзор", command=self.browse_file)
        self.browse_button.grid(row=0, column=1, padx=5, pady=5)
        
        # Фрейм для настроек анализа
        settings_frame = ttk.LabelFrame(self, text="Настройки анализа")
        settings_frame.pack(fill="x", padx=10, pady=10, expand=False)
        
        # Настройка минимальной длины слова
        ttk.Label(settings_frame, text="Минимальная длина слова:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.min_length_var = tk.IntVar(value=3)
        self.min_length_spinbox = ttk.Spinbox(settings_frame, from_=1, to=20, increment=1, textvariable=self.min_length_var, width=5)
        self.min_length_spinbox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Настройка количества слов для отображения
        ttk.Label(settings_frame, text="Количество слов в топе:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.top_words_var = tk.IntVar(value=20)
        self.top_words_spinbox = ttk.Spinbox(settings_frame, from_=5, to=100, increment=5, textvariable=self.top_words_var, width=5)
        self.top_words_spinbox.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Опция исключения стоп-слов
        self.exclude_stopwords_var = tk.BooleanVar(value=True)
        self.exclude_stopwords_check = ttk.Checkbutton(
            settings_frame, text="Исключить стоп-слова", 
            variable=self.exclude_stopwords_var
        )
        self.exclude_stopwords_check.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Кнопка для анализа
        self.analyze_button = ttk.Button(
            self, text="Выполнить анализ", 
            command=self.start_analysis
        )
        self.analyze_button.pack(pady=10)
        
        # Индикатор прогресса
        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="indeterminate")
        self.progress.pack(pady=5, fill="x", padx=10)
        
        # Фрейм для результатов
        results_frame = ttk.LabelFrame(self, text="Результаты анализа")
        results_frame.pack(fill="both", padx=10, pady=10, expand=True)
        
        # Создаем фрейм для графика
        self.plot_frame = ttk.Frame(results_frame)
        self.plot_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
        
        # Создаем фрейм для таблицы
        self.table_frame = ttk.Frame(results_frame)
        self.table_frame.pack(side=tk.RIGHT, fill="both", expand=False, padx=5, pady=5)
        
        # Создаем таблицу результатов
        columns = ("слово", "частота", "процент")
        self.results_tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=15)
        
        # Настройка заголовков
        self.results_tree.heading("слово", text="Слово")
        self.results_tree.heading("частота", text="Частота")
        self.results_tree.heading("процент", text="Процент")
        
        # Настройка столбцов
        self.results_tree.column("слово", width=120)
        self.results_tree.column("частота", width=80, anchor="center")
        self.results_tree.column("процент", width=80, anchor="center")
        
        # Добавляем scrollbar для таблицы
        tree_scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Размещаем элементы
        self.results_tree.pack(side=tk.LEFT, fill="both", expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill="y")
        
        # Кнопка для сохранения результатов
        self.save_button = ttk.Button(
            results_frame, text="Сохранить результаты", 
            command=self.save_results,
            state=tk.DISABLED
        )
        self.save_button.pack(pady=5)
        
        # Делаем первую колонку растягиваемой
        file_frame.columnconfigure(0, weight=1)
        
        # Русские стоп-слова
        self.russian_stopwords = [
            "а", "без", "более", "бы", "был", "была", "были", "было", "быть", "в", 
            "вам", "вас", "весь", "во", "вот", "все", "всего", "всех", "вы", "где", 
            "да", "даже", "для", "до", "его", "ее", "если", "есть", "еще", "же", 
            "за", "здесь", "и", "из", "или", "им", "их", "к", "как", "ко", 
            "когда", "кто", "ли", "либо", "мне", "может", "мы", "на", "надо", "наш", 
            "не", "него", "нее", "нет", "ни", "но", "ну", "о", "об", "однако", 
            "он", "она", "они", "оно", "от", "очень", "по", "под", "при", "с", 
            "со", "так", "также", "такой", "там", "те", "тем", "то", "того", "тоже", 
            "той", "только", "том", "ты", "у", "уже", "хотя", "чего", "чей", "чем", 
            "что", "чтобы", "этого", "этой", "этом", "этот", "эту", "я"
        ]
        
        # Данные для графика и таблицы
        self.analysis_results = None
    
    def browse_file(self):
        """Открывает диалог выбора файла"""
        filetypes = [
            ("Текстовые файлы", "*.txt"), 
            ("Все файлы", "*.*")
        ]
        
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.file_var.set(filename)
    
    def start_analysis(self):
        """Запускает частотный анализ в отдельном потоке"""
        file_path = self.file_var.get()
        if not file_path:
            messagebox.showerror("Ошибка", "Выберите файл для анализа!")
            return
        
        # Проверяем существование файла
        if not os.path.exists(file_path):
            messagebox.showerror("Ошибка", "Указанный файл не существует!")
            return
        
        # Получаем настройки
        try:
            min_length = int(self.min_length_var.get())
            top_words = int(self.top_words_var.get())
            
            if min_length <= 0:
                raise ValueError("Минимальная длина слова должна быть положительным числом")
                
            if top_words <= 0:
                raise ValueError("Количество слов в топе должно быть положительным числом")
                
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные настройки анализа: {str(e)}")
            return
        
        # Очищаем предыдущие результаты
        self.clear_results()
        
        # Запускаем прогресс-бар
        self.progress.start()
        
        # Блокируем кнопку анализа
        self.analyze_button.config(state=tk.DISABLED)
        
        # Запускаем анализ в отдельном потоке
        analyze_thread = threading.Thread(
            target=self.perform_analysis,
            args=(file_path, min_length, top_words, self.exclude_stopwords_var.get())
        )
        analyze_thread.daemon = True
        analyze_thread.start()
    
    def perform_analysis(self, file_path, min_length, top_words, exclude_stopwords):
        """Выполняет частотный анализ текста"""
        try:
            # Читаем файл
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            # Приводим текст к нижнему регистру
            text = text.lower()
            
            # Удаляем пунктуацию и заменяем её пробелами
            text = re.sub(r'[^\w\s]', ' ', text)
            
            # Разбиваем на слова
            words = text.split()
            
            # Фильтруем слова по длине
            words = [word for word in words if len(word) >= min_length]
            
            # Исключаем стоп-слова если нужно
            if exclude_stopwords:
                words = [word for word in words if word not in self.russian_stopwords]
            
            # Подсчитываем частоту слов
            word_counts = Counter(words)
            
            # Получаем общее количество слов
            total_words = len(words)
            
            # Получаем наиболее часто встречающиеся слова
            most_common_words = word_counts.most_common(top_words)
            
            # Создаем список для хранения результатов анализа: (слово, частота, процент)
            results = []
            for word, count in most_common_words:
                percent = (count / total_words) * 100
                results.append((word, count, percent))
            
            # Обновляем интерфейс в основном потоке
            self.after(0, lambda: self.update_results(results, total_words))
            
        except Exception as e:
            # Обрабатываем ошибки
            error_message = f"Ошибка при анализе: {str(e)}"
            self.after(0, lambda: self.show_analysis_error(error_message))
    
    def show_analysis_error(self, error_message):
        """Показывает ошибку анализа в главном потоке Tkinter."""
        messagebox.showerror("Ошибка", error_message)
        self.progress.stop()
        self.analyze_button.config(state=tk.NORMAL)

    def update_results(self, results, total_words):
        """Обновляет отображение результатов анализа"""
        # Останавливаем прогресс-бар
        self.progress.stop()
        
        # Разблокируем кнопку анализа
        self.analyze_button.config(state=tk.NORMAL)
        
        # Сохраняем результаты для использования в других методах
        self.analysis_results = results

        # Добавляем данные в таблицу
        for word, count, percent in results:
            self.results_tree.insert("", "end", values=(word, count, f"{percent:.2f}%"))
        
        # Строим гистограмму
        self.create_frequency_plot(results)
        
        # Активируем кнопку сохранения
        self.save_button.config(state=tk.NORMAL)
        
        # Вывод общей информации
        messagebox.showinfo("Анализ завершен", 
                          f"Анализ успешно завершен.\nВсего слов в тексте: {total_words}\n"
                          f"Отображено топ {len(results)} слов.")
    
    def create_frequency_plot(self, results):
        """Создает гистограмму частотности слов"""
        # Очищаем предыдущий график
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        
        # Подготавливаем данные для графика (берем только 10 самых частых слов для наглядности)
        plot_data = results[:10]
        words = [item[0] for item in plot_data]
        frequencies = [item[1] for item in plot_data]
        
        # Создаем фигуру и оси
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Строим горизонтальную гистограмму
        bars = ax.barh(words, frequencies, color='skyblue')
        
        # Добавляем значения на гистограмму
        for i, bar in enumerate(bars):
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                    f'{frequencies[i]}', va='center')
        
        # Настраиваем график
        ax.set_title('Топ 10 самых частых слов')
        ax.set_xlabel('Частота')
        ax.set_ylabel('Слово')
        
        # Инвертируем ось Y, чтобы самые частые слова были сверху
        ax.invert_yaxis()
        
        # Настраиваем поля
        fig.tight_layout()
        
        # Создаем холст для отображения графика в Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # Рисуем график
        canvas.draw()
    
    def clear_results(self):
        """Очищает предыдущие результаты анализа"""
        # Очищаем таблицу
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Очищаем график
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        
        # Сбрасываем результаты
        self.analysis_results = None
        
        # Деактивируем кнопку сохранения
        self.save_button.config(state=tk.DISABLED)
    
    def save_results(self):
        """Сохраняет результаты анализа в файл"""
        if not self.analysis_results:
            return
        
        # Открываем диалог сохранения файла
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                # Записываем заголовок
                file.write("Слово\tЧастота\tПроцент\n")
                
                # Записываем данные
                for word, count, percent in self.analysis_results:
                    file.write(f"{word}\t{count}\t{percent:.2f}%\n")
            
            messagebox.showinfo("Сохранение результатов", 
                              f"Результаты успешно сохранены в файл:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", 
                               f"Не удалось сохранить результаты: {str(e)}")


class WordCloudFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Создаем элементы интерфейса
        self.create_widgets()
    
    def create_widgets(self):
        # Фрейм для выбора файла
        file_frame = ttk.LabelFrame(self, text="Выбор файла")
        file_frame.pack(fill="x", padx=10, pady=10, expand=False)
        
        # Поле для отображения выбранного файла
        self.file_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_var, width=60)
        self.file_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Кнопка для выбора файла
        self.browse_button = ttk.Button(file_frame, text="Обзор", command=self.browse_file)
        self.browse_button.grid(row=0, column=1, padx=5, pady=5)
        
        # Фрейм для настроек облака слов
        settings_frame = ttk.LabelFrame(self, text="Настройки")
        settings_frame.pack(fill="x", padx=10, pady=10, expand=False)
        
        # Настройка минимальной длины слова
        ttk.Label(settings_frame, text="Минимальная длина слова:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.min_length_var = tk.IntVar(value=3)
        self.min_length_spinbox = ttk.Spinbox(settings_frame, from_=1, to=20, increment=1, textvariable=self.min_length_var, width=5)
        self.min_length_spinbox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Настройка максимального количества слов
        ttk.Label(settings_frame, text="Максимальное количество слов:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.max_words_var = tk.IntVar(value=200)
        self.max_words_spinbox = ttk.Spinbox(settings_frame, from_=50, to=1000, increment=50, textvariable=self.max_words_var, width=5)
        self.max_words_spinbox.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Выбор цветовой схемы
        ttk.Label(settings_frame, text="Цветовая схема:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        self.colormap_var = tk.StringVar(value="viridis")
        self.colormap_combo = ttk.Combobox(settings_frame, textvariable=self.colormap_var, width=15)
        self.colormap_combo['values'] = ('viridis', 'plasma', 'inferno', 'magma', 'cividis', 
                                          'Blues', 'Greens', 'Reds', 'YlOrBr', 'RdPu',
                                          'rainbow', 'hsv', 'jet')
        self.colormap_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Опция исключения стоп-слов
        self.exclude_stopwords_var = tk.BooleanVar(value=True)
        self.exclude_stopwords_check = ttk.Checkbutton(
            settings_frame, text="Исключить стоп-слова", 
            variable=self.exclude_stopwords_var
        )
        self.exclude_stopwords_check.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Кнопка для генерации облака слов
        self.generate_button = ttk.Button(
            self, text="Создать облако слов", 
            command=self.start_generation
        )
        self.generate_button.pack(pady=10)
        
        # Индикатор прогресса
        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="indeterminate")
        self.progress.pack(pady=5, fill="x", padx=10)
        
        # Фрейм для отображения облака слов
        self.wordcloud_frame = ttk.LabelFrame(self, text="Облако слов")
        self.wordcloud_frame.pack(fill="both", padx=10, pady=10, expand=True)
        
        # Фрейм для размещения изображения
        self.image_frame = ttk.Frame(self.wordcloud_frame)
        self.image_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Кнопка для сохранения облака слов
        self.save_button = ttk.Button(
            self.wordcloud_frame, text="Сохранить изображение", 
            command=self.save_wordcloud,
            state=tk.DISABLED
        )
        self.save_button.pack(pady=5)
        
        # Делаем первую колонку растягиваемой
        file_frame.columnconfigure(0, weight=1)
        
        # Русские стоп-слова
        self.russian_stopwords = [
            "а", "без", "более", "бы", "был", "была", "были", "было", "быть", "в", 
            "вам", "вас", "весь", "во", "вот", "все", "всего", "всех", "вы", "где", 
            "да", "даже", "для", "до", "его", "ее", "если", "есть", "еще", "же", 
            "за", "здесь", "и", "из", "или", "им", "их", "к", "как", "ко", 
            "когда", "кто", "ли", "либо", "мне", "может", "мы", "на", "надо", "наш", 
            "не", "него", "нее", "нет", "ни", "но", "ну", "о", "об", "однако", 
            "он", "она", "они", "оно", "от", "очень", "по", "под", "при", "с", 
            "со", "так", "также", "такой", "там", "те", "тем", "то", "того", "тоже", 
            "той", "только", "том", "ты", "у", "уже", "хотя", "чего", "чей", "чем", 
            "что", "чтобы", "этого", "этой", "этом", "этот", "эту", "я"
        ]
        
        # Сохраняем последнее созданное облако слов
        self.wordcloud_image = None
    
    def browse_file(self):
        """Открывает диалог выбора файла"""
        filetypes = [
            ("Текстовые файлы", "*.txt"), 
            ("Все файлы", "*.*")
        ]
        
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.file_var.set(filename)
    
    def start_generation(self):
        """Запускает генерацию облака слов в отдельном потоке"""
        file_path = self.file_var.get()
        if not file_path:
            messagebox.showerror("Ошибка", "Выберите файл для анализа!")
            return
        
        # Проверяем существование файла
        if not os.path.exists(file_path):
            messagebox.showerror("Ошибка", "Указанный файл не существует!")
            return
        
        # Получаем настройки
        try:
            min_length = int(self.min_length_var.get())
            max_words = int(self.max_words_var.get())
            colormap = self.colormap_var.get()
            
            if min_length <= 0:
                raise ValueError("Минимальная длина слова должна быть положительным числом")
                
            if max_words <= 0:
                raise ValueError("Максимальное количество слов должно быть положительным числом")
                
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные настройки: {str(e)}")
            return
        
        # Очищаем предыдущие результаты
        self.clear_results()
        
        # Запускаем прогресс-бар
        self.progress.start()
        
        # Блокируем кнопку генерации
        self.generate_button.config(state=tk.DISABLED)
        
        # Запускаем генерацию в отдельном потоке
        generate_thread = threading.Thread(
            target=self.generate_wordcloud,
            args=(file_path, min_length, max_words, colormap, self.exclude_stopwords_var.get())
        )
        generate_thread.daemon = True
        generate_thread.start()
    
    def generate_wordcloud(self, file_path, min_length, max_words, colormap, exclude_stopwords):
        """Генерирует облако слов из текста"""
        try:
            # Читаем файл
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            # Приводим текст к нижнему регистру
            text = text.lower()
            
            # Определяем стоп-слова
            stopwords = self.russian_stopwords if exclude_stopwords else None
            
            # Генерируем облако слов
            wordcloud = WordCloud(
                width=800, 
                height=500, 
                max_words=max_words,
                background_color='white',
                colormap=colormap,
                min_word_length=min_length,
                stopwords=stopwords,
                collocations=False,
                # Указываем шрифт, который поддерживает кириллицу
                font_path=None  # WordCloud автоматически выберет подходящий шрифт
            ).generate(text)
            
            # Обновляем интерфейс в основном потоке
            self.after(0, lambda: self.display_wordcloud(wordcloud))
            
        except Exception as e:
            # Обрабатываем ошибки
            error_message = f"Ошибка при создании облака слов: {str(e)}"
            self.after(0, lambda: self.show_wordcloud_error(error_message))
    
    def show_wordcloud_error(self, error_message):
        """Показывает ошибку генерации облака в главном потоке Tkinter."""
        messagebox.showerror("Ошибка", error_message)
        self.progress.stop()
        self.generate_button.config(state=tk.NORMAL)

    def display_wordcloud(self, wordcloud):
        """Отображает сгенерированное облако слов"""
        # Сохраняем созданное облако слов
        self.wordcloud_image = wordcloud

        # Останавливаем прогресс-бар
        self.progress.stop()
        
        # Разблокируем кнопку генерации
        self.generate_button.config(state=tk.NORMAL)
        
        # Очищаем предыдущее изображение
        for widget in self.image_frame.winfo_children():
            widget.destroy()
        
        # Создаем matplotlib фигуру
        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        # Отображаем облако слов
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')  # Скрываем оси
        
        # Создаем холст для отображения в Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.image_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # Рисуем облако слов
        canvas.draw()
        
        # Активируем кнопку сохранения
        self.save_button.config(state=tk.NORMAL)
        
        # Показываем сообщение об успешном завершении
        messagebox.showinfo("Облако слов создано", 
                           "Облако слов успешно создано.")
    
    def clear_results(self):
        """Очищает предыдущие результаты"""
        # Очищаем фрейм с изображением
        for widget in self.image_frame.winfo_children():
            widget.destroy()
        
        # Сбрасываем облако слов
        self.wordcloud_image = None
        
        # Деактивируем кнопку сохранения
        self.save_button.config(state=tk.DISABLED)
    
    def save_wordcloud(self):
        """Сохраняет сгенерированное облако слов в файл"""
        if not self.wordcloud_image:
            return
        
        # Открываем диалог сохранения файла
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG файлы", "*.png"), ("Все файлы", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Сохраняем изображение
            self.wordcloud_image.to_file(file_path)
            
            messagebox.showinfo("Сохранение облака слов", 
                              f"Облако слов успешно сохранено в файл:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", 
                               f"Не удалось сохранить облако слов: {str(e)}")