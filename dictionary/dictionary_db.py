from dict_parse import *


if __name__ == '__main__':
    all_words = parse()
    with open('dictionary.txt', 'w', encoding='utf-8') as file:

        for i in all_words:
            print(i)
            file.write(i + '\n')