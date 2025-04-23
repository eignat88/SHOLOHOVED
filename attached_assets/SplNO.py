import os

# Функция для чтения и обработки входного файла
def process_input_file(input_file):
    sections = {}  # Словарь для хранения разделов

    with open(input_file, 'r', encoding='utf-8') as file:
        current_section = None

        for line in file:
            line = line.strip()

            if line.isdigit() and len(line) == 4:
                # Найдено новое начало раздела
                current_section = line
                sections[current_section] = []
            elif current_section is not None:
                # Строка принадлежит текущему разделу
                sections[current_section].append(line)

    return sections

# Функция для сохранения разделов в отдельные файлы
def save_sections(sections):
    for section, content in sections.items():
        output_file = f"{section}.txt"
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write('\n'.join(content))

# Главная функция программы
def main(input_file):
    if os.path.isfile(input_file):
        sections = process_input_file(input_file)
        if sections:
            save_sections(sections)
            print("Разделы успешно сохранены.")
        else:
            print("Входной файл не содержит разделов.")
    else:
        print("Входной файл не найден.")

if __name__ == "__main__":
    input_file = "Тихий Дон. Михаил Шолохов.txt"
    main(input_file)