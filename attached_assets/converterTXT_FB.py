from bs4 import BeautifulSoup
import os

def get_current_directory():
    return os.path.abspath(os.path.dirname(__file__))

def txt_to_fb2(txt_file_path, fb2_file_path):
    with open(txt_file_path, 'r', encoding='utf-8') as txt_file:
        txt_content = txt_file.read()

    soup = BeautifulSoup(features='xml')
    soup.append(soup.new_tag("FictionBook", xmlns="http://www.gribuser.ru/xml/fictionbook/2.0"))
    fiction_book = soup.FictionBook
    description = soup.new_tag("description")
    title_info = soup.new_tag("title-info")

    title = soup.new_tag("book-title")
    title.string = os.path.basename(txt_file_path)
    author = soup.new_tag("author")
    author_name = soup.new_tag("first-name")
    author_name.string = "Your Author Name"
    author.append(author_name)

    title_info.append(title)
    title_info.append(author)
    description.append(title_info)
    fiction_book.append(description)

    body = soup.new_tag("body")
    section = soup.new_tag("section")
    title = soup.new_tag("title")
    title.string = os.path.basename(txt_file_path)
    p = soup.new_tag("p")
    p.string = txt_content

    section.append(title)
    section.append(p)
    body.append(section)
    fiction_book.append(body)

    with open(fb2_file_path, 'w', encoding='utf-8') as fb2_file:
        fb2_file.write(str(soup))

def convert_txt_files_to_fb2(directory_path):
    if not os.path.exists(directory_path):
        print(f"Directory not found: {directory_path}")
        return

    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            txt_file_path = os.path.join(directory_path, filename)
            fb2_file_path = os.path.splitext(txt_file_path)[0] + ".fb2"
            txt_to_fb2(txt_file_path, fb2_file_path)
            print(f"Converted {txt_file_path} to {fb2_file_path}")

if __name__ == "__main__":
    current_directory = get_current_directory()
    txt_directory = current_directory  # Используем текущую директорию

    convert_txt_files_to_fb2(txt_directory)
