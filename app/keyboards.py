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

def create_inline_button(text: str, callback_data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=callback_data)

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

MONTHS = [
    "Янв", "Фев", "Мар", "Апр", "Май", "Июн",
    "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"
]

def get_period_keyboard(selected: list[tuple[int, int]], year: int) -> InlineKeyboardMarkup:
    keyboard = []

    # Верхняя навигация по годам
    keyboard.append([
        InlineKeyboardButton(text='←', callback_data="year_prev"),
        InlineKeyboardButton(text=str(year), callback_data="noop"),
        InlineKeyboardButton(text="→", callback_data="year_next"),
    ])

    # Получаем границы выделения
    sorted_sel = sorted(selected)
    if len(sorted_sel) == 2:
        y1, m1 = sorted_sel[0]
        y2, m2 = sorted_sel[1]
        def in_range(yy, mm):
            return (y1, m1) <= (yy, mm) <= (y2, m2)
    else:
        def in_range(yy, mm):
            return (yy, mm) in selected

    # Месяцы
    row = []
    for i, month in enumerate(MONTHS, 1):
        if in_range(year, i):
            label = f"{month} ✅"
        else:
            label = month
        row.append(InlineKeyboardButton(text=label, callback_data=f"month_{i}_{year}"))
        if i % 3 == 0:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(text="Сформировать", callback_data="submit_period")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
