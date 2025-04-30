import sqlite3
from contextlib import closing


def create_database():
    with closing(sqlite3.connect('database.db')) as connection:
        cursor = connection.cursor()

        # Таблица со словами
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Words (
            id INTEGER PRIMARY KEY,
            word VARCHAR(256) NOT NULL UNIQUE 
        )
        ''')

        # Таблица пользователей
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY,
            telegram_id INTEGER UNIQUE NOT NULL  
        )
        ''')

        # Связующая таблица для отношений многие-ко-многим
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserWords (
            user_id INTEGER NOT NULL,
            word_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, word_id),
            FOREIGN KEY (user_id) REFERENCES Users(id),
            FOREIGN KEY (word_id) REFERENCES Words(id)
        )
        ''')

        # Создаем индексы для ускорения поиска
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_words ON Words(word)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_words ON UserWords(user_id)')

        connection.commit()

def add_user(telegram_id):
    with closing(sqlite3.connect('database.db')) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO Users (telegram_id) VALUES (?)', (telegram_id,))
        conn.commit()


def add_word_to_user(telegram_id, word):
    with closing(sqlite3.connect('database.db')) as conn:
        cursor = conn.cursor()

        # Добавляем слово в общий словарь
        cursor.execute('INSERT OR IGNORE INTO Words (word) VALUES (?)', (word,))

        # Получаем ID созданных сущностей
        cursor.execute('SELECT id FROM Users WHERE telegram_id = ?', (telegram_id,))
        user_id = cursor.fetchone()[0]

        cursor.execute('SELECT id FROM Words WHERE word = ?', (word,))
        word_id = cursor.fetchone()[0]

        # Связываем пользователя и слово
        cursor.execute('INSERT OR IGNORE INTO UserWords (user_id, word_id) VALUES (?, ?)', (user_id, word_id))
        conn.commit()

def get_user_words(telegram_id):
    with closing(sqlite3.connect('database.db')) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT w.word 
            FROM UserWords uw
            JOIN Users u ON uw.user_id = u.id
            JOIN Words w ON uw.word_id = w.id
            WHERE u.telegram_id = ?
        ''', (telegram_id,))
        return [row[0] for row in cursor.fetchall()]


def get_random_word(telegram_id):
    """Возвращает случайное слово, которого нет у пользователя"""
    with closing(sqlite3.connect('database.db')) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT w.word 
            FROM Words w
            WHERE NOT EXISTS (
                SELECT 1 
                FROM UserWords uw
                JOIN Users u ON uw.user_id = u.id 
                WHERE u.telegram_id = ? 
                AND uw.word_id = w.id
            )
            ORDER BY RANDOM() 
            LIMIT 1
        ''', (telegram_id,))

        result = cursor.fetchone()
        return result[0] if result else None

def add_words():
    with open('C:/Users/loban/PycharmProjects/EngRusBot/dictionary/dictionary.txt', 'r', encoding='utf-8') as f:
        with closing(sqlite3.connect('database.db')) as conn:
            cursor = conn.cursor()
            for i in f.readlines():
                cursor.execute('''
                INSERT OR IGNORE INTO Words (word) VALUES (?)
                ''', (i[:len(i) - 2], ))

            conn.commit()

def main():
    create_database()
    add_words()


if __name__ == '__main__':
    main()