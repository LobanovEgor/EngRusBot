import requests
from bs4 import BeautifulSoup


def get_links():
    url = "https://wooordhunt.ru/dic/content/en_ru" #Берём страницу с гиперссылками
    response = requests.get(url)
    all_links = [] #Здесь будем хранить наши ссылки на страницы словаря
    html_text = BeautifulSoup(response.text, 'html.parser')
    div_content = html_text.find('div', id='content') # Находим тег где хранятся все ссылки
    links = div_content.find_all('a') # Получаем все теги вида <a href='*ссылка*'

    for link in links:
        all_links.append(link.get('href')) # Добавляем ссылку в список

    return all_links

def get_words(link):
    url = "https://wooordhunt.ru" + link # Подставляем нужную гиперссылку
    response = requests.get(url)
    all_words = [] # Здесь будем хранить все слова
    html_text = BeautifulSoup(response.text, 'html.parser')
    div_content = html_text.find('div', id='content') # Находим div с тегами p где находятся слова
    tag_p = div_content.find_all('p') # Также находим тег со всеми словами
    for word in tag_p:
        text = word.text
        all_words.append(text) # Вытаскиваем текст из тега и добавляем в список

    return all_words

def parse():
    links = get_links() # Собираем ссылки
    words = []

    for link in links:
        from_link = get_words(link) # Получаем список слов
        for i in from_link:
            words.append(i)

    return words
