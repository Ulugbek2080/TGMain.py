import sqlite3
import tracemalloc
from aiogram import F, Router
from aiogram import types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, CallbackQuery
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


@router.message(CommandStart())
async def cmd_start(message: Message):
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

    text = message.text
    language_map = {
        'Русский язык 🇷🇺': 'ru',
        'English language 🇬🇧': 'en',
        '中文 🇨🇳': 'ch',
        "O'zbek tili 🇺🇿": 'uz'
    }
    user = message.from_user
    telegram_id = str(user.id)  # Важно: преобразуем в строку, если поле в базе GUID
    username = user.username or ''
    first_name = user.first_name or ''
    last_name = user.last_name or ''

    selected_lang = language_map.get(text, 'ru')
    AddLan(telegram_id, selected_lang)
    user_id = message.from_user.id
    await state.update_data(user_id=user_id, language=selected_lang)

    Result  = DATA_BaseTG.check_and_add_user(telegram_id, username, first_name, last_name)

    PolitikaBota = slovar.get_dictionary('ПрочитатьПолитикуБота', selected_lang)
    reply_markup = kb.get_consent_keyboard(selected_lang)

    await message.answer(
        PolitikaBota,
        reply_markup=reply_markup)
    file_path = TovariZap
    try:
        doc = FSInputFile(file_path, filename="Offer.docx")
        await message.answer_document(document=doc)
    except Exception as e:
        print(f"Ошибка отправки документа: {e}")

#Получение контакта
@router.message(F.contact)
async def some_handler(message: Message, state: FSMContext):
    Dostup = Check_Client(message.contact.phone_number)
    Dostup = True
    if Dostup:
        after_auth = slovar.get_dictionary('ПриветствиеПослеАвторизации', lang)
        reply_markup = kb.get_main_menu_keyboard(lang)
        await message.answer(after_auth, reply_markup=reply_markup)
    else:
        Text = slovar.get_dictionary('НеНайденКонтакт', lang)
        await message.answer(Text)


@router.message(F.text == slovar.get_dictionary('Согласен', lang))
async def handle_agree(message: Message, state: FSMContext):
    lang = languageUser(message.from_user.id)
    await message.answer(
        slovar.get_dictionary('Приветствие', lang),
        reply_markup=kb.get_contact_request_keyboard(lang)
    )


@router.message(F.text== slovar.get_dictionary('НеДаюСогласия', lang))
async def handle_disagree(message: Message, state: FSMContext):
    lang = languageUser(message.from_user.id)

    await message.answer(

        slovar.get_dictionary('ТекстПользовательНеДалСоглаия', lang),

        reply_markup=kb.get_consent_keyboard(lang)

    )


@router.message(F.text== slovar.get_dictionary('Отчеты', lang))
async def handle_reports(message: Message):
    lang = languageUser(message.from_user.id)

    await message.answer(

        slovar.get_dictionary('ВыборДействия', lang),

        reply_markup=kb.get_report_keyboard(lang)

    )


@router.message(F.text== slovar.get_dictionary('Сервисы', lang))
async def handle_services(message: Message):
    lang = languageUser(message.from_user.id)

    await message.answer(

        slovar.get_dictionary('ВыборДействия', lang),

        reply_markup=kb.get_services_keyboard(lang)

    )


@router.message(F.text== slovar.get_dictionary('Назад',lang))
async def handle_back(message: Message):
    lang = languageUser(message.from_user.id)

    await message.answer(

        slovar.get_dictionary('ВыборДействия', lang),

        reply_markup=kb.get_main_menu_keyboard(lang)

    )

@router.message(F.text== slovar.get_dictionary('ПомощьОператора', lang))
async def handle_operator_help(message: Message):
    await message.bot.send_contact(
        chat_id=message.chat.id,
        phone_number=config.phone,
        first_name=config.first_name,
    )
    #Товары

def get_kods_from_db(user_id: int) -> list[str]:
    conn = DATA_BaseTG.get_connection()  # или pyodbc.connect(...)
    cursor = conn.cursor()

    cursor.execute("SELECT Код FROM TelegramChats WHERE ИД = ?", (str(user_id),))
    rows = cursor.fetchall()

    conn.close()

    # Получаем только список значений кодов
    kods = [row[0] for row in rows if row[0] is not None]
    return kods

@router.message(F.text== slovar.get_dictionary('ТоварыВПути', lang))
async def handle_goods_on_the_way(message: Message):
    lang = languageUser(message.from_user.id)
    user_id = message.from_user.id
    # Получаем список кодов
    kods = get_kods_from_db(user_id)
    kod_buttons = get_inline_keyboard_Kod(kods)
    kod_text = slovar.get_dictionary('ВыборКодов', lang)
    await message.answer(kod_text, reply_markup=kod_buttons)


@router.callback_query(F.data.startswith("kod_"))
async def handle_kod_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    kod = callback.data.removeprefix("kod_")

    try:
        file_path = DATA_BaseTG.Tovari_v_Puti(int(kod))  # Добавляем код!
        doc = FSInputFile(file_path)

        await callback.message.answer_document(
            document=doc,
            caption=f"📦 Отчет по товарам в пути: {kod}"
        )
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при формировании отчета: {e}")

@router.message(F.text==slovar.get_dictionary('ВсеТовары', lang))
async def handle_all_goods(message: Message, state: FSMContext):
    pdf_path = DATA_BaseTG.Vse_tovari()
    doc = FSInputFile(pdf_path)
    await message.answer_document(
        document=doc,
        caption="Все товары"
    )

@router.message(F.text== slovar.get_dictionary('ПрибывшиеТовары', lang))
async def handle_arrived_goods(message: Message):
    doc = FSInputFile(DATA_BaseTG.Pribivshie_tovati())
    await message.answer_document(
        document=doc,
        caption="📦 Отчет по товарам в пути"
    )

@router.message(F.text== slovar.get_dictionary('ПолученныеТовары', lang))
async def handle_received_goods(message: Message):
    doc = FSInputFile(DATA_BaseTG.Poluchennie_tovari())
    await message.answer_document(
        document=doc,
        caption="📦 Отчет по товарам в пути"
    )

@router.message(F.text== slovar.get_dictionary('МоиКоды', lang))
async def handle_my_codes(message: Message):
    await message.answer("🔐 Ваши коды:")
    # Товары

    # Скалды
@router.message(F.text== slovar.get_dictionary('АдресаСкладов', lang))
async def handle_warehouses(message: Message):
    lang = languageUser(message.from_user.id)
    await message.answer(
        slovar.get_dictionary('ТекстДляАдресовСклада', lang),
        reply_markup=build_keyboard(message.from_user.id)
    )

@router.message(
    F.text== slovar.get_dictionary('СписокЗапрещенныхТоваров', lang))
async def handle_banned_goods(message: Message):
    doc = FSInputFile(TovariZap, filename="Список запрещенных товаров.docx")
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

def languageUser(id):
    lang = DATA_BaseTG.Check_lan(id)
    return lang

def AddLan(id, lang):
    lang = DATA_BaseTG.update_language_by_telegram_id(id, lang)

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