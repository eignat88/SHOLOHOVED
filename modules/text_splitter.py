import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import re

class TextSplitterTab(ttk.Frame):
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
        
        # Фрейм для настройки разделения
        settings_frame = ttk.LabelFrame(self, text="Настройки разделения")
        settings_frame.pack(fill="x", padx=10, pady=10, expand=False)
        
        ttk.Label(settings_frame, text="Шаблон для разделения:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Варианты разделения
        self.split_type = tk.StringVar(value="number")
        
        self.number_radio = ttk.Radiobutton(
            settings_frame, text="По 4-значным числам", 
            variable=self.split_type, value="number"
        )
        self.number_radio.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.custom_radio = ttk.Radiobutton(
            settings_frame, text="По шаблону:", 
            variable=self.split_type, value="custom"
        )
        self.custom_radio.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        self.pattern_var = tk.StringVar()
        self.pattern_entry = ttk.Entry(settings_frame, textvariable=self.pattern_var, width=40)
        self.pattern_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Кнопка для запуска разделения текста
        self.split_button = ttk.Button(
            self, text="Разделить текст", 
            command=self.start_splitting
        )
        self.split_button.pack(pady=10)
        
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
        
        # Делаем первую колонку растягиваемой
        file_frame.columnconfigure(0, weight=1)
        settings_frame.columnconfigure(1, weight=1)
    
    def browse_file(self):
        """Открывает диалог выбора файла"""
        filetypes = [
            ("Текстовые файлы", "*.txt"), 
            ("Все файлы", "*.*")
        ]
        
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.file_var.set(filename)
    
    def start_splitting(self):
        """Запускает процесс разделения текста в отдельном потоке"""
        file_path = self.file_var.get()
        if not file_path:
            messagebox.showerror("Ошибка", "Выберите файл для разделения!")
            return
        
        # Проверяем существование файла
        if not os.path.exists(file_path):
            messagebox.showerror("Ошибка", "Указанный файл не существует!")
            return
        
        # Проверяем настройки разделения
        split_type = self.split_type.get()
        
        if split_type == "custom" and not self.pattern_var.get():
            messagebox.showerror("Ошибка", "Введите шаблон для разделения!")
            return
        
        # Очищаем поле статуса
        self.status_text.delete(1.0, tk.END)
        self.update_status("Начало разделения текста...")
        
        # Запускаем прогресс-бар
        self.progress.start()
        
        # Запускаем разделение в отдельном потоке
        split_thread = threading.Thread(
            target=self.perform_splitting,
            args=(file_path, split_type, self.pattern_var.get())
        )
        split_thread.daemon = True
        split_thread.start()
    
    def perform_splitting(self, file_path, split_type, custom_pattern):
        """Выполняет разделение текста"""
        try:
            # Определяем шаблон для разделения
            if split_type == "number":
                pattern = r'^\d{4}$'
            else:
                pattern = custom_pattern
            
            self.update_status(f"Использую шаблон: {pattern}")
            
            # Словарь для хранения разделов
            sections = {}
            
            # Чтение и обработка входного файла
            self.update_status("Чтение и обработка файла...")
            
            with open(file_path, 'r', encoding='utf-8') as file:
                current_section = None
                
                for line in file:
                    line = line.strip()
                    
                    if split_type == "number":
                        # Для 4-значных чисел используем простую проверку
                        if line.isdigit() and len(line) == 4:
                            current_section = line
                            sections[current_section] = []
                        elif current_section is not None:
                            sections[current_section].append(line)
                    else:
                        # Для пользовательского шаблона используем регулярные выражения
                        if re.match(pattern, line):
                            current_section = line
                            sections[current_section] = []
                        elif current_section is not None:
                            sections[current_section].append(line)
            
            # Если нет разделов, выводим ошибку
            if not sections:
                self.after(100, lambda: self.update_status("Входной файл не содержит разделов по заданному шаблону!"))
                self.after(100, lambda: self.progress.stop())
                return
            
            # Сохраняем разделы в отдельные файлы
            self.update_status(f"Сохранение {len(sections)} разделов в отдельные файлы...")
            
            output_dir = os.path.dirname(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            saved_files = []
            
            for section, content in sections.items():
                # Формируем имя выходного файла
                output_file = os.path.join(output_dir, f"{base_name}_{section}.txt")
                
                # Сохраняем раздел в файл
                with open(output_file, 'w', encoding='utf-8') as file:
                    file.write('\n'.join(content))
                
                saved_files.append(output_file)
            
            # Обновляем статус в основном потоке
            self.after(100, lambda: self.splitting_completed(saved_files))
            
        except Exception as e:
            # Обрабатываем ошибки
            error_message = f"Ошибка при разделении текста: {str(e)}"
            self.after(100, lambda: self.update_status(error_message))
            self.after(100, lambda: self.progress.stop())
    
    def splitting_completed(self, saved_files):
        """Обрабатывает завершение разделения текста"""
        self.progress.stop()
        self.update_status(f"Разделение текста завершено успешно!")
        self.update_status(f"Создано файлов: {len(saved_files)}")
        
        for file in saved_files[:5]:  # Показываем только первые 5 файлов
            self.update_status(f"- {os.path.basename(file)}")
        
        if len(saved_files) > 5:
            self.update_status(f"... и еще {len(saved_files) - 5} файлов")
        
        if messagebox.askyesno("Разделение завершено", 
                              "Разделение завершено успешно. Открыть папку с результатами?"):
            # Открываем папку в проводнике
            os.system(f'explorer "{os.path.dirname(saved_files[0])}"')
    
    def update_status(self, message):
        """Обновляет текстовое поле статуса"""
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)  # Прокрутка вниз
