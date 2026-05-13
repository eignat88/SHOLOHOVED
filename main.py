import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys

# Убедимся, что модули находятся в пути поиска
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импорт наших модулей
from modules.fb2_converter import FB2ConverterTab
from modules.reading_time import ReadingTimeTab
from modules.docx_converter import DocxConverterTab
from modules.text_analyzer import TextAnalyzerTab
from modules.text_splitter import TextSplitterTab
from modules.text_statistics import TextStatisticsTab

class MultiTextApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Многофункциональное приложение для обработки текста")
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Создаем систему вкладок
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Добавляем все вкладки с функциональностью
        self.fb2_converter_tab = FB2ConverterTab(self.notebook)
        self.notebook.add(self.fb2_converter_tab, text="Конвертация в FB2")
        
        self.reading_time_tab = ReadingTimeTab(self.notebook)
        self.notebook.add(self.reading_time_tab, text="Время чтения")
        
        self.docx_converter_tab = DocxConverterTab(self.notebook)
        self.notebook.add(self.docx_converter_tab, text="Конвертация DOCX")
        
        self.text_analyzer_tab = TextAnalyzerTab(self.notebook)
        self.notebook.add(self.text_analyzer_tab, text="Анализ текста")
        
        self.text_splitter_tab = TextSplitterTab(self.notebook)
        self.notebook.add(self.text_splitter_tab, text="Разделение текста")
        
        # Вкладка статистического анализа текста
        self.text_statistics_tab = TextStatisticsTab(self.notebook)
        self.notebook.add(self.text_statistics_tab, text="Статистика текста")

        # Создаем строку состояния
        self.status_var = tk.StringVar()
        self.status_var.set("Готово")
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Настройка стилей
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", font=("Helvetica", 10))
        self.style.configure("TLabel", font=("Helvetica", 10))
        self.style.configure("TEntry", font=("Helvetica", 10))
        
        # Установка обработчика закрытия окна
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def update_status(self, message):
        """Обновляет сообщение в строке состояния"""
        self.status_var.set(message)
        self.update_idletasks()
    
    def on_closing(self):
        """Обработчик закрытия окна"""
        if messagebox.askokcancel("Выход", "Вы действительно хотите выйти?"):
            self.destroy()

if __name__ == "__main__":
    try:
        # Отключаем вывод NLTK при загрузке
        import nltk.downloader
        nltk.downloader._show_info = lambda *args, **kwargs: None
        
        # Загружаем токенизатор NLTK
        import nltk
        nltk.download('punkt', quiet=True)
        
        app = MultiTextApp()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Возникла непредвиденная ошибка: {str(e)}")
