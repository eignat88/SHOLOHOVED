import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading

class ReadingTimeTab(ttk.Frame):
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
        
        # Фрейм для настроек расчета времени чтения
        settings_frame = ttk.LabelFrame(self, text="Настройки")
        settings_frame.pack(fill="x", padx=10, pady=10, expand=False)
        
        # Настройка скорости чтения (слов в минуту)
        ttk.Label(settings_frame, text="Скорость чтения (слов в минуту):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.wpm_var = tk.IntVar(value=200)
        self.wpm_spinbox = ttk.Spinbox(settings_frame, from_=50, to=1000, increment=10, textvariable=self.wpm_var, width=5)
        self.wpm_spinbox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Кнопка для расчета времени чтения
        self.calculate_button = ttk.Button(
            self, text="Рассчитать время чтения", 
            command=self.start_calculation
        )
        self.calculate_button.pack(pady=10)
        
        # Индикатор прогресса
        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="indeterminate")
        self.progress.pack(pady=5, fill="x", padx=10)
        
        # Рамка для отображения результатов
        results_frame = ttk.LabelFrame(self, text="Результаты")
        results_frame.pack(fill="both", padx=10, pady=10, expand=True)
        
        # Поля для отображения результатов
        self.total_words_var = tk.StringVar(value="Всего слов: 0")
        self.reading_time_var = tk.StringVar(value="Время чтения: 0 мин. 0 сек.")
        
        ttk.Label(results_frame, textvariable=self.total_words_var, font=("Helvetica", 12)).pack(pady=10)
        ttk.Label(results_frame, textvariable=self.reading_time_var, font=("Helvetica", 12)).pack(pady=10)
        
        # Делаем первую колонку растягиваемой
        file_frame.columnconfigure(0, weight=1)
        settings_frame.columnconfigure(0, weight=1)
    
    def browse_file(self):
        """Открывает диалог выбора файла"""
        filetypes = [
            ("Текстовые файлы", "*.txt"), 
            ("Все файлы", "*.*")
        ]
        
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.file_var.set(filename)
    
    def start_calculation(self):
        """Запускает расчет времени чтения в отдельном потоке"""
        file_path = self.file_var.get()
        if not file_path:
            messagebox.showerror("Ошибка", "Выберите файл для анализа!")
            return
        
        # Проверяем существование файла
        if not os.path.exists(file_path):
            messagebox.showerror("Ошибка", "Указанный файл не существует!")
            return
        
        # Очищаем результаты
        self.total_words_var.set("Всего слов: расчет...")
        self.reading_time_var.set("Время чтения: расчет...")
        
        # Получаем скорость чтения
        try:
            wpm = int(self.wpm_var.get())
            if wpm <= 0:
                raise ValueError("Скорость чтения должна быть положительным числом")
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректное значение для скорости чтения!")
            return
        
        # Запускаем прогресс-бар
        self.progress.start()
        
        # Запускаем расчет в отдельном потоке
        calc_thread = threading.Thread(
            target=self.calculate_reading_time,
            args=(file_path, wpm)
        )
        calc_thread.daemon = True
        calc_thread.start()
    
    def calculate_reading_time(self, file_path, words_per_minute):
        """Выполняет расчет времени чтения"""
        try:
            # Читаем файл
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            # Разбиваем текст на слова
            words = text.split()
            
            # Подсчитываем количество слов в тексте
            num_words = len(words)
            
            # Рассчитываем время чтения в минутах
            reading_time_minutes = num_words / words_per_minute
            
            # Преобразуем время в формат минут и секунд
            minutes = int(reading_time_minutes)
            seconds = int((reading_time_minutes - minutes) * 60)
            
            # Обновляем интерфейс в основном потоке
            self.after(100, lambda: self.update_results(num_words, minutes, seconds))
            
        except Exception as e:
            # Обрабатываем ошибки
            error_message = f"Ошибка при расчете: {str(e)}"
            self.after(100, lambda: messagebox.showerror("Ошибка", error_message))
            self.after(100, lambda: self.progress.stop())
    
    def update_results(self, num_words, minutes, seconds):
        """Обновляет отображение результатов"""
        self.progress.stop()
        self.total_words_var.set(f"Всего слов: {num_words}")
        self.reading_time_var.set(f"Время чтения: {minutes} мин. {seconds} сек.")
