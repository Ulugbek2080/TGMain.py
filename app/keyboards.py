from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import app.slovar as slovar
import app.http_request as http_request
from datetime import datetime
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_language_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Русский язык 🇷🇺"),
                KeyboardButton(text="English language 🇬🇧")
            ],
            [
                KeyboardButton(text="中文 🇨🇳"),
                KeyboardButton(text="O'zbek tili 🇺🇿")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите языка"
    )
    return keyboard

def get_main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    text_reports = slovar.get_dictionary("Отчеты", lang)
    text_services = slovar.get_dictionary("Сервисы", lang)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=text_reports),
                KeyboardButton(text=text_services)
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )
    return keyboard

def get_report_keyboard(lang: str, has_high_priority: bool = True, has_medium_priority: bool = True) -> ReplyKeyboardMarkup:
    # Получаем тексты кнопок на нужном языке
    text_goods_in_transit = slovar.get_dictionary("ТоварыВПути", lang)
    text_all_goods = slovar.get_dictionary("ВсеТовары", lang)
    text_arrived_goods = slovar.get_dictionary("ПрибывшиеТовары", lang)
    text_received_goods = slovar.get_dictionary("ПолученныеТовары", lang)
    text_my_codes = slovar.get_dictionary("МоиКоды", lang)
    text_back = slovar.get_dictionary("Назад", lang)

    keyboard = []

    # Первая строка: Товары в пути + Все товары (только если высокий приоритет)
    row1 = [KeyboardButton(text=text_goods_in_transit)]
    if has_high_priority:
        row1.append(KeyboardButton(text=text_all_goods))
    keyboard.append(row1)

    # Вторая строка: Прибывшие товары + Полученные товары (только если высокий приоритет)
    row2 = [KeyboardButton(text=text_arrived_goods)]
    if has_high_priority:
        row2.append(KeyboardButton(text=text_received_goods))
    keyboard.append(row2)

    # Третья строка: Мои коды
    keyboard.append([KeyboardButton(text=text_my_codes)])

    # Четвёртая строка: Назад
    keyboard.append([KeyboardButton(text=text_back)])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder=slovar.get_dictionary("ВыборДействия", lang)
    )

def get_services_keyboard(lang: str) -> ReplyKeyboardMarkup:
    # Получаем переводы
    text_addresses = slovar.get_dictionary("АдресаСкладов", lang)
    text_help = slovar.get_dictionary("ПомощьОператора", lang)
    text_banned =slovar.get_dictionary("СписокЗапрещенныхТоваров", lang)
    text_back = slovar.get_dictionary("Назад", lang)

    keyboard = [
        [
            KeyboardButton(text=text_addresses),
            KeyboardButton(text=text_help)
        ],
        [KeyboardButton(text=text_banned)],
        [KeyboardButton(text=text_back)]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder=slovar.get_dictionary("ВыборДействия", lang)
    )

def get_consent_keyboard(lang: str) -> ReplyKeyboardMarkup:
    text_agree = slovar.get_dictionary("Согласен", lang)
    text_disagree = slovar.get_dictionary("НеДаюСогласия", lang)

    keyboard = [
        [
            KeyboardButton(text=text_agree),
            KeyboardButton(text=text_disagree)
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder=slovar.get_dictionary("ПрочитатьПолитикуБота", lang)
    )

def get_inline_keyboard_sklad() -> InlineKeyboardMarkup:
    #data = http_request.get_http_skladi()
    #build_keyboard
    return True


def get_inline_keyboard_MyCodes() -> InlineKeyboardMarkup:
    data = http_request.get_http_MyCodes()
    return InlineKeyboardMarkup(inline_keyboard=data)

async def build_date_selection_keyboard(user_input: str, state: FSMContext, lang: str) -> InlineKeyboardMarkup:
    data = await state.get_data()
    selected_dates = data.get("selected_dates", [])

    # Определим год, который будет в заголовке
    current_year = datetime.today().year
    current_month = datetime.today().month

    if user_input.startswith("YearL_") or user_input.startswith("YearR_") or user_input.startswith("YearY_"):
        base_date = datetime.strptime(user_input.split("_")[1], "%Y%m%d")
        if "YearL_" in user_input:
            current_year = base_date.year - 1
        elif "YearR_" in user_input:
            current_year = base_date.year + 1
        else:
            current_year = base_date.year

    # Верхняя строка – год и стрелки
    year_row = [
        create_inline_button("<", f"YearL_{current_year}0101"),
        create_inline_button(str(current_year), f"YearY_{current_year}0101"),
        create_inline_button(">", f"YearR_{current_year}0101")
    ]

    # Месяцы
    month_buttons = []
    for month in range(1, 13):
        date_code = f"{current_year}{month:02}01"
        readable_date = datetime(current_year, month, 1)
        month_name = slovar.get_dictionary(readable_date.strftime("%B"), lang)

        if date_code in selected_dates:
            text = f"✅ {month_name}"
            callback_data = f"TimM_{date_code}"  # Убираем
        else:
            text = month_name
            callback_data = f"TimN_{date_code}"  # Добавляем

        month_buttons.append(create_inline_button(text, callback_data))

    # Разбиваем на строки по 3 кнопки
    month_rows = [month_buttons[i:i+3] for i in range(0, len(month_buttons), 3)]

    # Последняя кнопка "Сформировать"
    finish_text = slovar.get_dictionary("СФормировать", lang)
    finish_button = [create_inline_button(finish_text, "Sformirovat_")]

    return InlineKeyboardMarkup(
        inline_keyboard=[year_row] + month_rows + [finish_button]
    )

def create_inline_button(text: str, callback_data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=callback_data)

async def handle_month_selection(callback_data: str, state: FSMContext):
    data = await state.get_data()
    selected_dates = set(data.get("selected_dates", []))

    if callback_data.startswith("TimM_"):  # убрать
        date_str = callback_data.replace("TimM_", "")
        selected_dates.discard(date_str)
    elif callback_data.startswith("TimN_"):  # добавить
        date_str = callback_data.replace("TimN_", "")
        selected_dates.add(date_str)

    # Обновим в состоянии
    await state.update_data(selected_dates=list(selected_dates))

def get_contact_request_keyboard(lang: str) -> ReplyKeyboardMarkup:
    contact_text = slovar.get_dictionary("КнопкаОтправкаНомераТелефона", lang)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=contact_text, request_contact=True)
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder=contact_text
    )
    return keyboard

def get_inline_keyboard_Kod(kods) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=str(kod), callback_data=f"kod_{kod}")] for kod in kods
    ])
    return keyboard


