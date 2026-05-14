import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import nltk
from bs4 import BeautifulSoup

class FB2ConverterTab(ttk.Frame):
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
        
        # Фрейм для конвертации файлов
        options_frame = ttk.LabelFrame(self, text="Параметры конвертации")
        options_frame.pack(fill="x", padx=10, pady=10, expand=False)
        
        # Радиокнопки для выбора типа конвертации
        self.convert_type = tk.StringVar(value="txt_to_fb2")
        
        self.txt_to_fb2_radio = ttk.Radiobutton(
            options_frame, text="TXT в FB2", 
            variable=self.convert_type, value="txt_to_fb2"
        )
        self.txt_to_fb2_radio.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.docx_to_fb2_radio = ttk.Radiobutton(
            options_frame, text="DOCX в FB2", 
            variable=self.convert_type, value="docx_to_fb2"
        )
        self.docx_to_fb2_radio.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        # Кнопка для запуска конвертации
        self.convert_button = ttk.Button(
            self, text="Конвертировать", 
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
        convert_type = self.convert_type.get()
        
        if convert_type == "txt_to_fb2":
            filetypes = [("Текстовые файлы", "*.txt")]
        elif convert_type == "docx_to_fb2":
            filetypes = [("DOCX файлы", "*.docx")]
        
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
        
        # Очищаем поле статуса
        self.status_text.delete(1.0, tk.END)
        self.update_status("Начало конвертации...")
        
        # Запускаем прогресс-бар
        self.progress.start()
        
        # Запускаем конвертацию в отдельном потоке
        convert_type = self.convert_type.get()
        convert_thread = threading.Thread(
            target=self.perform_conversion,
            args=(file_path, convert_type)
        )
        convert_thread.daemon = True
        convert_thread.start()
    
    def perform_conversion(self, file_path, convert_type):
        """Выполняет конвертацию файла"""
        try:
            if convert_type == "txt_to_fb2":
                output_file = self.txt_to_fb2(file_path)
            elif convert_type == "docx_to_fb2":
                output_file = self.docx_to_fb2(file_path)
            
            # Отображаем успешное завершение
            self.after(0, lambda: self.conversion_completed(output_file))
            
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
            # Открытие файла в браузере или программе по умолчанию
            output_file_url = f'file:///{os.path.normpath(os.path.abspath(output_file)).replace(os.sep, "/")}'
            os.system(f'start "" "{output_file_url}"')
    
    def update_status(self, message):
        """Обновляет текстовое поле статуса"""
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)  # Прокрутка вниз

    def post_status(self, message):
        """Планирует обновление статуса в главном потоке Tkinter."""
        self.after(0, lambda message=message: self.update_status(message))
    
    def txt_to_fb2(self, txt_file_path):
        """Конвертирует TXT файл в FB2 формат"""
        self.post_status("Чтение текстового файла...")
        
        # Чтение текстового файла
        with open(txt_file_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        # Токенизация текста
        self.post_status("Обработка текста...")
        tokens = nltk.word_tokenize(text)
        
        lines = []
        current_line = []
        for token in tokens:
            current_line.append(token)
            if len(current_line) >= 25:
                lines.append(' '.join(current_line))
                current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Получаем имя файла без расширения
        file_name = os.path.splitext(os.path.basename(txt_file_path))[0]
        
        # Формируем имя выходного файла
        output_file_name = f"{file_name}_formatted.fb2"
        
        # Генерация FB2 файла через BeautifulSoup
        self.post_status("Создание FB2 файла...")
        
        soup = BeautifulSoup(features='xml')
        soup.append(soup.new_tag("FictionBook", xmlns="http://www.gribuser.ru/xml/fictionbook/2.0"))
        fiction_book = soup.FictionBook
        
        # Метаданные
        description = soup.new_tag("description")
        title_info = soup.new_tag("title-info")
        
        book_title = soup.new_tag("book-title")
        book_title.string = file_name
        title_info.append(book_title)
        
        author = soup.new_tag("author")
        author_name = soup.new_tag("first-name")
        author_name.string = "Автор"
        author.append(author_name)
        title_info.append(author)
        
        description.append(title_info)
        fiction_book.append(description)
        
        # Тело документа
        body = soup.new_tag("body")
        section = soup.new_tag("section")
        
        for line in lines:
            p = soup.new_tag("p")
            p.string = line
            section.append(p)
        
        body.append(section)
        fiction_book.append(body)
        
        # Сохраняем результат в FB2
        with open(output_file_name, 'w', encoding='utf-8') as file:
            file.write(str(soup))
        
        self.post_status(f"FB2 файл сохранен как '{output_file_name}'")
        return output_file_name
    
    def docx_to_fb2(self, docx_file_path):
        """Конвертирует DOCX файл в FB2 формат"""
        self.post_status("Чтение DOCX файла...")
        
        try:
            from docx import Document
            from xml.sax.saxutils import escape
            
            # Открываем DOCX файл
            doc = Document(docx_file_path)
            
            # Получаем имя файла без расширения
            file_name = os.path.splitext(os.path.basename(docx_file_path))[0]
            
            # Формируем имя выходного файла
            output_file_name = f"{file_name}.fb2"
            
            self.post_status("Создание FB2 файла...")
            
            # Открываем файл для записи в формате FB2
            with open(output_file_name, "w", encoding="utf-8") as fb2_file:
                # Записываем начало документа FB2
                fb2_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                fb2_file.write('<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" xmlns:l="http://www.w3.org/1999/xlink">\n')
                
                # Записываем метаинформацию о книге
                fb2_file.write('<description>\n')
                fb2_file.write('<title-info>\n')
                fb2_file.write(f'<book-title>{escape(file_name)}</book-title>\n')
                fb2_file.write('<author>\n')
                fb2_file.write('<first-name>Автор</first-name>\n')
                fb2_file.write('<last-name></last-name>\n')
                fb2_file.write('</author>\n')
                fb2_file.write('</title-info>\n')
                fb2_file.write('</description>\n')
                
                fb2_file.write('<body>\n')
                
                # Перебираем все параграфы в документе DOCX
                for paragraph in doc.paragraphs:
                    # Экранируем специальные символы в тексте и записываем его в FB2
                    fb2_file.write('<p>' + escape(paragraph.text) + '</p>\n')
                
                # Закрываем документ FB2
                fb2_file.write('</body>\n')
                fb2_file.write('</FictionBook>')
            
            self.post_status(f"FB2 файл сохранен как '{output_file_name}'")
            return output_file_name
            
        except ImportError:
            self.post_status("Ошибка: модуль python-docx не установлен")
            raise Exception("Для конвертации DOCX файлов требуется модуль python-docx. Установите его командой: pip install python-docx")
