from docx import Document
from xml.sax.saxutils import escape

def docx_to_fb2(input_file, output_file):
    # Открываем DOCX файл
    doc = Document(input_file)

    # Открываем файл для записи в формате FB2
    with open(output_file, "w", encoding="utf-8") as fb2_file:
        # Записываем начало документа FB2
        fb2_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        fb2_file.write('<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" xmlns:l="http://www.w3.org/1999/xlink">\n')

        # Записываем метаинформацию о книге
        fb2_file.write('<description>\n')
        fb2_file.write('<title-info>\n')
        fb2_file.write('<book-title>Название вашей книги</book-title>\n')
        fb2_file.write('<author>\n')
        fb2_file.write('<first-name>Имя автора</first-name>\n')
        fb2_file.write('<last-name>Фамилия автора</last-name>\n')
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

# Пути к файлам
input_file = "sholokhov-tikhii-don_GLZ.docx"
output_file = "sholokhov-tikhii-don_GLZ.fb2"

# Конвертируем DOCX в FB2
docx_to_fb2(input_file, output_file)
