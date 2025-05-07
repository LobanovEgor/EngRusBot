from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from commands.keyboard import all_kb
from commands.keyboard.all_kb import user_dict_kb
from database import database as db
from database.database import get_random_word, add_word_to_user, get_user_words, add_skipped_word

router = Router()
@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer('Добро пожаловать! Этот бот нужен для создания собственного англо-русского словаря!',
                         reply_markup=all_kb.main_kb())
    await db.add_user(message.from_user.id)



class States(StatesGroup):
    waiting_for_input = State()  # Состояние ожидания ввода слова
    waiting_for_approve = State()
    choose_pages = State()

# Обработчик кнопки "Добавить слово"
@router.message(F.text.lower() == '📝 добавить слово')
async def add_word(message: Message, state: FSMContext):
    await message.answer("Введите слово и его перевод через тире (например: apple - яблоко)")
    await state.set_state(States.waiting_for_input)  # Устанавливаем состояние ожидания


# Обработчик ввода данных
@router.message(States.waiting_for_input)
async def process_word_input(message: Message, state: FSMContext):
        # Проверяем формат ввода
        if "-" not in message.text:
            await message.answer("❌ Ошибка формата! Используйте тире между словом и переводом.")
            return

        # Разделяем слово и перевод
        word = message.text
        id = message.from_user.id

        await db.add_word_to_user(
            telegram_id=id,
            word=word
        )

        await message.answer(f"✅ Добавлено: {word}")
        await state.clear()  # Выходим из состояния

@router.message(F.text.lower() == '🎲 случайное слово')
async def rand_word(message: Message, state: FSMContext):
    word = await get_random_word(message.from_user.id)
    await message.answer(f'{word}', reply_markup=all_kb.approve_kb())
    await state.set_state(States.waiting_for_approve)
    await state.update_data(current_word=word)

@router.callback_query(F.data == 'add_word', States.waiting_for_approve)
async def approve_word(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    word = data['current_word']
    await add_word_to_user(callback.from_user.id, word)
    await callback.message.answer(text=f'✅ Слово "{word[0:word.find("—") - 1]}" добавлено в ваш словарь!')
    await state.clear()
    await callback.answer()
    await callback.message.delete()

@router.callback_query(F.data == 'skip_word', States.waiting_for_approve)
async def skip_word(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    word = data['current_word']
    await add_skipped_word(callback.from_user.id, word)
    await callback.message.answer("⏩ Слово пропущено.")
    await state.clear()
    await callback.answer()
    await callback.message.delete()


@router.message(F.text.lower() == '📚 мой словарь')
async def user_words(message: Message, state: FSMContext):
    # Получаем все слова пользователя
    all_words = await get_user_words(message.from_user.id)

    # Сохраняем в состоянии: текущая страница, общее количество страниц, список слов
    await state.update_data(
        page=0,
        total_pages=(len(all_words) + 9) // 10,  # Округление вверх для подсчета страниц
        all_words=all_words
    )

    # Формируем текст первой страницы
    current_data = await state.get_data()
    page = current_data['page']
    words_chunk = current_data['all_words'][page * 10: (page + 1) * 10]

    words_text = "\n\n".join([f"{i + 1}. {word}" for i, word in enumerate(words_chunk, start=page * 10)])

    # Отправляем сообщение с пагинацией
    await message.answer(
        f"📚 Ваш словарь (страница {page + 1}/{current_data['total_pages']}):\n\n{words_text}",
        reply_markup=user_dict_kb(has_previous=False, has_next=current_data['total_pages'] > 1)
    )
    await state.set_state(States.choose_pages)


@router.callback_query(F.data.in_(['next_page', 'prev_page']), States.choose_pages)
async def handle_pagination(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data['page']
    total_pages = data['total_pages']
    all_words = data['all_words']

    # Определяем новую страницу
    new_page = current_page + 1 if callback.data == 'next_page' else current_page - 1

    # Проверяем границы
    if new_page < 0 or new_page >= total_pages:
        await callback.answer("Больше страниц нет!")
        return

    # Обновляем состояние
    await state.update_data(page=new_page)

    # Получаем слова для новой страницы
    words_chunk = all_words[new_page * 10: (new_page + 1) * 10]
    words_text = "\n\n".join([f"{i + 1}. {word}" for i, word in enumerate(words_chunk, start=new_page * 10)])

    # Обновляем клавиатуру
    updated_kb = user_dict_kb(
        has_previous=new_page > 0,
        has_next=new_page < total_pages - 1
    )

    # Редактируем существующее сообщение
    await callback.message.edit_text(
        f"📚 Ваш словарь (страница {new_page + 1}/{total_pages}):\n\n{words_text}",
        reply_markup=updated_kb
    )
    await callback.answer()

@router.callback_query(F.data == 'quit')
async def quit_dict(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()