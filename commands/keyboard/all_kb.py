from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


def main_kb():
    kb_list = [[KeyboardButton(text='🎲 Случайное слово'), KeyboardButton(text='📝 Добавить слово')],
        [KeyboardButton(text='📚 Мой словарь')]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)
    return keyboard

def approve_kb():
    kb_list = [[InlineKeyboardButton(text='✅ Добавить слово', callback_data='add_word'),
                InlineKeyboardButton(text='🚫 Пропустить слово', callback_data='skip_word')]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)
    return keyboard

def user_dict_kb(has_previous: bool, has_next: bool) -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(text="Закончить", callback_data='quit')]
    if has_previous:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data="prev_page"))
    if has_next:
        buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data="next_page"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])