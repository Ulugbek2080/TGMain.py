from pathlib import Path

from aiogram import F, Router
from aiogram import types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, CallbackQuery, TelegramObject
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.keyboards import *

import app.DATA_Base as DATA_BaseTG
import app.keyboards as kb
import app.slovar as slovar

from config_data.config import Config, load_config

config: Config = load_config()
sklady = DATA_BaseTG.get_all_sklady()
user_selection = {}  # user_id -> set of selected GUIDs
router = Router()
TovariZap = config.tovari_put
lang = 'ru'
user_periods: dict[int, list[tuple[int, int]]] = {}
user_id = None
last_word = "Все Товары"


@router.message(CommandStart())
async def cmd_start(message: Message):
    global user_id
    user_id = message.from_user.id
    await message.answer(
        'Добро пожаловать! Выберите язык \nWelcome! Select a language',
        reply_markup=kb.get_language_keyboard())

@router.message(F.text.in_([
    'Русский язык 🇷🇺',
    'English language 🇬🇧',
    '中文 🇨🇳',
    "O'zbek tili 🇺🇿"
]))
async def language_selected(message: Message, state: FSMContext):
    global lang, TovariZap
    text = message.text
    language_map = {
        'Русский язык 🇷🇺': 'ru',
        'English language 🇬🇧': 'en',
        '中文 🇨🇳': 'ch',
        "O'zbek tili 🇺🇿": 'uz'
    }

    selected_lang = language_map.get(text, 'ru')
    lang = language_map.get(text, 'ru')
    user_id = message.from_user.id
    await state.update_data(user_id=user_id, language=selected_lang)



    PolitikaBota = slovar.get_dictionary('ПрочитатьПолитикуБота', selected_lang)
    reply_markup = kb.get_consent_keyboard(selected_lang)

    await message.answer(
        PolitikaBota,
        reply_markup=reply_markup)
    try:
        file_path = Path(config.tovari_put.tovari_put)
        doc = FSInputFile(file_path)
        await message.answer_document(document=doc)
    except Exception as e:
        print(f"Ошибка отправки документа: {e}")

#Получение контакта
@router.message(F.contact)
async def some_handler(message: Message, state: FSMContext):
    Dostup = Check_Client(message.contact.phone_number)
    Dostup = True
    if Dostup:
        user = message.from_user
        telegram_id = str(user.id)  # Важно: преобразуем в строку, если поле в базе GUID
        username = user.username or ''
        first_name = user.first_name or ''
        last_name = user.last_name or ''
        Result  = DATA_BaseTG.check_and_add_user(telegram_id, username, first_name, last_name, message.contact.phone_number)
        after_auth = slovar.get_dictionary('ПриветствиеПослеАвторизации', lang)
        reply_markup = kb.get_main_menu_keyboard(lang)
        await message.answer(after_auth, reply_markup=reply_markup)
    else:
        Text = slovar.get_dictionary('НеНайденКонтакт', lang)
        await message.answer(Text)


@router.message(F.text == slovar.get_dictionary('Согласен', lang))
async def handle_agree(message: Message, state: FSMContext):

    await message.answer(
        slovar.get_dictionary('Приветствие', lang),
        reply_markup=kb.get_contact_request_keyboard(lang)
    )


@router.message(F.text== slovar.get_dictionary('НеДаюСогласия', lang))
async def handle_disagree(message: Message, state: FSMContext):


    await message.answer(

        slovar.get_dictionary('ТекстПользовательНеДалСоглаия', lang),

        reply_markup=kb.get_consent_keyboard(lang)

    )


@router.message(F.text== slovar.get_dictionary('Отчеты', lang))
async def handle_reports(message: Message):


    await message.answer(

        slovar.get_dictionary('ВыборДействия', lang),

        reply_markup=kb.get_report_keyboard(lang)

    )


@router.message(F.text== slovar.get_dictionary('Сервисы', lang))
async def handle_services(message: Message):

    await message.answer(
        slovar.get_dictionary('ВыборДействия', lang),
        reply_markup=kb.get_services_keyboard(lang)
    )


@router.message(F.text== slovar.get_dictionary('Назад',lang))
async def handle_back(message: Message):

    await message.answer(

        slovar.get_dictionary('ВыборДействия', lang),

        reply_markup=kb.get_main_menu_keyboard(lang)

    )

@router.message(F.text== slovar.get_dictionary('ПомощьОператора', lang))
async def handle_operator_help(message: Message):
    await message.bot.send_contact(
        chat_id=message.chat.id,
        phone_number=str(config.phone),
        first_name=config.first_name.first_name,
    )
    #Товары

def get_kods_from_db(user_id: int) -> list[str]:
    conn = DATA_BaseTG.get_connection()  # или pyodbc.connect(...)
    cursor = conn.cursor()
    cursor.execute("SELECT НомерТелефона FROM TelegramChats WHERE Ид = ?", (user_id,))
    telefon_numbers=cursor.fetchone()
    cleaned_numbers = [number[1:] for number in telefon_numbers]
    cursor.execute("SELECT КодКлиента FROM ТелефоныКлиентов WHERE Телефон = ?", (cleaned_numbers))
    rows = cursor.fetchall()

    conn.close()

    # Получаем только список значений кодов
    kods = [row[0] for row in rows if row[0] is not None]
    return kods

@router.message(F.text == slovar.get_dictionary('ТоварыВПути', lang))
async def handle_goods_on_the_way(message: Message):
    # Получаем список кодов
    await Otchyt('ТоварыВПути', message)

async def Otchyt(word:str, message: TelegramObject):
    global last_word
    kods = get_kods_from_db(message.from_user.id)
    kod_buttons = get_inline_keyboard_Kod(kods)
    kod_text = slovar.get_dictionary('ВыборКодов', lang)
    last_word = slovar.get_dictionary(f'{word}', lang)
    await message.answer(kod_text, reply_markup=kod_buttons)

@router.callback_query(F.data.startswith("kod_"))
async def handle_kod_callback(callback: CallbackQuery):
    global last_word
    user_id = callback.from_user.id
    kod = callback.data.removeprefix("kod_")
    period = user_periods.get(user_id)
    statusi = None
    if period is None:
        if last_word== slovar.get_dictionary('ПрибывшиеТовары', lang):
            statusi = "5"
        elif last_word == slovar.get_dictionary('ТоварыВПути', lang):
            statusi = "1, 2, 3, 4"
        else:
            statusi = "6"
    else:
        statusi = "1, 2, 3, 4, 5, 6"
    file_path = DATA_BaseTG.Tovari_v_Puti(int(kod), period, statusi)  # Добавляем код!
    doc = FSInputFile(file_path)
    caption_text = slovar.get_dictionary(last_word, lang)
    await callback.message.answer_document(
        document=doc,
        caption=f"📦 {caption_text}: {kod}"
    )
@router.message(F.text==slovar.get_dictionary('ВсеТовары', lang))
async def handle_all_goods(message: Message, state: FSMContext):
    current_year = datetime.now().year
    await state.update_data(selected_months=[], year=current_year)
    kb = get_period_keyboard([], current_year)
    await message.answer("Выберите период:", reply_markup=kb)

@router.callback_query(F.data.startswith("year_"))
async def handle_year_change(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    year = data.get("year", datetime.now().year)
    if callback.data == "year_prev":
        year -= 1
    elif callback.data == "year_next":
        year += 1
    await state.update_data(year=year)
    kb = get_period_keyboard(data.get("selected", []), year)
    await callback.message.edit_reply_markup(reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("month_"))
async def handle_month_select(callback: CallbackQuery, state: FSMContext):
    _, m_str, y_str = callback.data.split("_")
    month = int(m_str)
    year = int(y_str)

    data = await state.get_data()
    selected: list[tuple[int, int]] = data.get("selected", [])

    current = (year, month)

    if current in selected:
        # Удаляем эту кнопку и оставляем только другую
        selected = [s for s in selected if s != current]
    elif len(selected) >= 2:
        # Если уже 2 выбраны — сбрасываем и ставим новую
        selected = [current]
    elif len(selected) == 1:
        selected.append(current)
    else:
        selected = [current]

    await state.update_data(selected=selected)
    kb = get_period_keyboard(selected, data.get("year", datetime.now().year))
    await callback.message.edit_reply_markup(reply_markup=kb)
    await callback.answer()



@router.callback_query(F.data == "submit_period")
async def handle_submit_period(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected: list[tuple[int, int]] = data.get("selected", [])

    if not selected:
        await callback.answer("Сначала выберите период", show_alert=True)
        return

    sorted_sel = sorted(selected)
    if len(sorted_sel) == 1:
        dates = [sorted_sel[0]]
    else:
        # Генерация всех месяцев между датами
        y1, m1 = sorted_sel[0]
        y2, m2 = sorted_sel[1]
        dates = []
        y, m = y1, m1
        while (y, m) <= (y2, m2):
            dates.append((y, m))
            if m == 12:
                m = 1
                y += 1
            else:
                m += 1

    user_id = callback.from_user.id
    user_periods[user_id] = dates
    # Получаем список кодов
    kods = get_kods_from_db(user_id)
    kod_buttons = get_inline_keyboard_Kod(kods)
    kod_text = slovar.get_dictionary('ВыборКодов', lang)
    await callback.message.answer(text=kod_text, reply_markup=kod_buttons)

@router.message(F.text== slovar.get_dictionary('ПрибывшиеТовары', lang))
async def handle_arrived_goods(message: Message):
    await Otchyt('ПрибывшиеТовары', message)
@router.message(F.text== slovar.get_dictionary('ПолученныеТовары', lang))
async def handle_received_goods(message: Message):
    await Otchyt('ПолученныеТовары', message)
@router.message(F.text== slovar.get_dictionary('МоиКоды', lang))
async def handle_my_codes(callback: CallbackQuery):
    conn = DATA_BaseTG.get_connection()  # или pyodbc.connect(...)
    cursor = conn.cursor()
    cursor.execute("SELECT НомерТелефона FROM TelegramChats WHERE Ид = ?", (user_id,))
    telefon_numbers = cursor.fetchone()
    file_path = DATA_BaseTG.MyKods(telefon_numbers)  # Добавляем код!
    doc = FSInputFile(file_path)

    await callback.message.answer_document(
        document=doc,
        caption=f"📦 {slovar.get_dictionary('ОтчетМоиКоды', lang)}"
    )
@router.message(F.text== slovar.get_dictionary('АдресаСкладов', lang))
async def handle_warehouses(message: Message):
    await message.answer(
        slovar.get_dictionary('ТекстДляАдресовСклада', lang),
        reply_markup=build_keyboard(message.from_user.id)
    )

@router.message(
    F.text== slovar.get_dictionary('СписокЗапрещенныхТоваров', lang))
async def handle_banned_goods(message: Message):
    doc = FSInputFile(str(TovariZap), filename="Список запрещенных товаров.docx")
    await message.answer_document(document=doc)
    # Скалды

#Область служебнные

@router.callback_query(lambda c: c.data.startswith("Sklal_") or c.data.startswith("Sklan_"))
async def toggle_sklad(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data
    guid = data.replace("Sklal_", "").replace("Sklan_", "")

    selected = user_selection.get(user_id, set())
    if guid in selected:
        selected.remove(guid)
    else:
        selected.add(guid)
    user_selection[user_id] = selected

    await callback.message.edit_reply_markup(reply_markup=build_keyboard(user_id))
    await callback.answer("Обновлено")

@router.callback_query(lambda c: c.data == "GetDataOnDedicatedWarehouses")
async def send_selected(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    selected = user_selection.get(user_id, set())

    if not selected:
        await callback.answer("Вы ничего не выбрали.", show_alert=True)
        return

    selected_sklady = [s for s in sklady if s["guid"] in selected]
    text = "Вы выбрали склады по адресам:\n\n"

    for sklad in selected_sklady:
        text = f"{sklad['name']}\n {sklad['address']}\n\n"
        await callback.message.answer(text)
    user_selection[user_id] = set()


def Check_Client(phone_number):
    Dostup = DATA_BaseTG.check_Client(phone_number)
    return Dostup

def build_keyboard(user_id):

    builder = InlineKeyboardBuilder()
    selected = user_selection.get(user_id, set())



    for sklad in sklady:
        guid = sklad["guid"]
        name = sklad["name"]
        is_selected = guid in selected

        mark = "✅" if is_selected else "⬜"
        callback_prefix = "Sklan_" if is_selected else "Sklal_"
        callback_data = callback_prefix + guid

        builder.button(text=mark, callback_data=callback_data)
        builder.button(text=name, callback_data=callback_data)

    builder.button(text="Получить данные", callback_data="GetDataOnDedicatedWarehouses")
    builder.adjust(2)  # 2 кнопки в строке

    return builder.as_markup()

#КонецОбласти