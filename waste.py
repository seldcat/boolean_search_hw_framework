import re

def split_string(input_string):
    # Используем регулярное выражение для разделения строки на слова и специальные символы
    tokens = re.findall(r'\w+|[()| ]', input_string)
    return tokens

# Пример использования
print(split_string("hello (world|fine)"))
print(split_string("(hello|fine|world) hello"))
