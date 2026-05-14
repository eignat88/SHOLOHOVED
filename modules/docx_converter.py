import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading

class DocxConverterTab(ttk.Frame):
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
        
        # Кнопка для конвертации
        self.convert_button = ttk.Button(
            self, text="Конвертировать DOCX в TXT", 
            command=self.start_conversion
        )
        self.convert_button.pack(pady=10)
        
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
    
    def browse_file(self):
        """Открывает диалог выбора файла"""
        filetypes = [("Word Files", "*.docx")]
        
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.file_var.set(filename)
    
    def start_conversion(self):
        """Запускает процесс конвертации в отдельном потоке"""
        file_path = self.file_var.get()
        if not file_path:
            messagebox.showerror("Ошибка", "Выберите файл для конвертации!")
            return
        
        # Проверяем существование файла
        if not os.path.exists(file_path):
            messagebox.showerror("Ошибка", "Указанный файл не существует!")
            return
        
        # Проверяем, является ли файл действительно DOCX
        if not file_path.lower().endswith('.docx'):
            messagebox.showerror("Ошибка", "Выбранный файл не является файлом DOCX!")
            return
        
        # Очищаем поле статуса
        self.status_text.delete(1.0, tk.END)
        self.update_status("Начало конвертации...")
        
        # Запускаем прогресс-бар
        self.progress.start()
        
        # Запускаем конвертацию в отдельном потоке
        convert_thread = threading.Thread(
            target=self.perform_conversion,
            args=(file_path,)
        )
        convert_thread.daemon = True
        convert_thread.start()
    
    def perform_conversion(self, file_path):
        """Выполняет конвертацию файла"""
        try:
            # Пытаемся импортировать модуль docx2txt
            try:
                import docx2txt
            except ImportError:
                self.post_status("Ошибка: модуль docx2txt не установлен")
                self.after(0, lambda: self.progress.stop())
                raise Exception("Для конвертации DOCX файлов требуется модуль docx2txt. Установите его командой: pip install docx2txt")
            
            # Конвертируем DOCX в текст
            self.post_status("Конвертация DOCX в текст...")
            text = docx2txt.process(file_path)
            
            # Получаем имя файла без расширения
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Формируем имя выходного файла
            output_file_name = f"{file_name}.txt"
            
            # Сохраняем результат в TXT
            with open(output_file_name, 'w', encoding='utf-8') as file:
                file.write(text)
            
            # Отображаем успешное завершение
            self.after(0, lambda: self.conversion_completed(output_file_name))
            
        except Exception as e:
            # Обрабатываем ошибки
            error_message = f"Ошибка конвертации: {str(e)}"
            self.post_status(error_message)
            self.after(0, lambda: self.progress.stop())
    
    def conversion_completed(self, output_file):
        """Обрабатывает завершение конвертации"""
        self.progress.stop()
        self.update_status(f"Конвертация завершена успешно!\nРезультат сохранен в: {output_file}")
        
        if messagebox.askyesno("Конвертация завершена", 
                               "Конвертация завершена успешно. Открыть файл?"):
            # Открываем файл в блокноте
            os.system(f'notepad.exe "{output_file}"')
    
    def update_status(self, message):
        """Обновляет текстовое поле статуса"""
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)  # Прокрутка вниз

    def post_status(self, message):
        """Планирует обновление статуса в главном потоке Tkinter."""
        self.after(0, lambda message=message: self.update_status(message))
