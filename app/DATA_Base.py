import math
import os
import random
from datetime import datetime
from datetime import timedelta

from aiogram.types import CallbackQuery
from fpdf import FPDF

import matplotlib.pyplot as plt
import pandas as pd
import pyodbc
from sqlalchemy import create_engine
from config_data.config import Config, load_config
from app import slovar
from app.keyboards import get_inline_keyboard_Kod

config: Config = load_config()

def create_table():
    create_table_chatId()
    create_table_tovary()
    create_Svedeniya_o_tovare()
    Create_Cliente()
    Create_Scladi()
    create_StatusiTovarov()

# Подключение к базе данных MSSQL
def get_connection():
    conn_str = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=Python_base_tg;'
        'UID=sa;'
        'PWD=1212'
    )
    return pyodbc.connect(conn_str)


# Создаем таблицы
def create_table_chatId():
    conn = get_connection()

    cursor = conn.cursor()

    create_table_query = '''
        IF OBJECT_ID('TelegramChats', 'U') IS NULL
        BEGIN
            CREATE TABLE TelegramChats (
                Код INT PRIMARY KEY,
                Наименование NVARCHAR(255),
                НомерТелефона NVARCHAR(20),
                Родитель INT,
                ЭтоГруппа BIT,
                ПометкаУдаления BIT,
                Предопределенный BIT,
                ИмяПредопределенныхДанных NVARCHAR(255),
                Ид NVARCHAR(255),
                чТип NVARCHAR(255),
                чЗаголовок NVARCHAR(255),
                чИнтернетИмя NVARCHAR(255),
                чИмя NVARCHAR(255),
                чФамилия NVARCHAR(255),
                пЭтоБот BIT,
                пИмя NVARCHAR(255),
                пФамилия NVARCHAR(255),
                пИнтернетИмя NVARCHAR(255),
                пКодЯзыка NVARCHAR(10),
                Ссылка NVARCHAR(255)
            )
        END
    '''

    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()

    print("Таблица создана успешно или уже существует.")

def create_table_tovary():
    conn = get_connection()
    cursor = conn.cursor()

    create_table_query = '''
        IF OBJECT_ID('Tovary', 'U') IS NULL
        BEGIN
            CREATE TABLE Tovary (
                ID INT PRIMARY KEY IDENTITY(1,1),
                Kod NVARCHAR(50),
            )
        END
    '''

    cursor.execute(create_table_query)
    conn.commit()
    conn.close()

def create_Svedeniya_o_tovare():
    conn = get_connection()
    cursor = conn.cursor()

    create_table_query = '''
            IF OBJECT_ID('Svedeniya_o_tovare', 'U') IS NULL
            BEGIN
                CREATE TABLE Svedeniya_o_tovare (
                    ID INT PRIMARY KEY IDENTITY(1,1),
                    TovarID INT FOREIGN KEY REFERENCES Tovary(ID),
                    TipUpakovki NVARCHAR(100),
                    VidTovara NVARCHAR(100),
                    Klient NVARCHAR(255),
                    Obem DECIMAL(18,3),
                    Ves DECIMAL(18,3),
                    Dlina DECIMAL(18,2),
                    Shirina DECIMAL(18,2),
                    Vysota DECIMAL(18,2),
                    NomerMesta NVARCHAR(50),
                    VsegoMest INT,
                    CenaZaKub DECIMAL(18,2),
                    CenaZaTonnu DECIMAL(18,2),
                    PoVesu BIT,
                    Summa DECIMAL(18,2),
                    VozvratTovara BIT,
                    EtoPochta BIT,
                    SummaBrend DECIMAL(18,2),
                    SummaZ DECIMAL(18,2),
                    DataDobavleniya DATETIME DEFAULT GETDATE()
                )
            END
        '''

    cursor.execute(create_table_query)
    conn.commit()
    conn.close()
    print("Таблица создана успешно или уже существует.")

def create_StatusiTovarov():
    conn = get_connection()
    cursor = conn.cursor()

    create_table_query = '''
        IF OBJECT_ID('StatusiTovarov', 'U') IS NULL
        BEGIN
            CREATE TABLE StatusiTovarov (
                ID INT PRIMARY KEY IDENTITY(1,1),
                Klient NVARCHAR(255),
                Statusy NVARCHAR(255),
                NomerOrdera NVARCHAR(50),
                KodKlienta NVARCHAR(50),
                TipUpakovki NVARCHAR(100),
                Mest INT,
                DataPriema DATE,
                SkladPriema NVARCHAR(255),
                VidTovara NVARCHAR(100),
                AdresMagazina NVARCHAR(255),
                TrekKod NVARCHAR(100),
                TelMagazina NVARCHAR(50),
                NaimenovanieMagazina NVARCHAR(255),
                Dlina DECIMAL(18,2),
                Shirina DECIMAL(18,2),
                Vysota DECIMAL(18,2),
                Tovar NVARCHAR(50),
                DneyVPuti INT,
                DataPribytiyaIliTekushchaya DATE,
                Obem DECIMAL(18,3),
                Ves DECIMAL(18,3),
                Cena DECIMAL(18,2),
                Status NVARCHAR(100),
                TochkaMarshruta NVARCHAR(100),
                Kommentariy NVARCHAR(MAX),
                DataPribytiya DATE,
                Summa DECIMAL(18,2),
                Sklad NVARCHAR(255),
                DataDobavleniya DATETIME DEFAULT GETDATE()
            )
        END
    '''

    cursor.execute(create_table_query)
    conn.commit()
    conn.close()
    print("Таблица создана успешно или уже существует.")

def Create_Cliente():
    conn = get_connection()
    cursor = conn.cursor()

    create_clients_table = '''
        IF OBJECT_ID('Клиенты', 'U') IS NULL
BEGIN
    CREATE TABLE Клиенты (
    КодКлиента INT PRIMARY KEY,
    ТипКода NVARCHAR(50),

    -- Первая роль
    Статус1 NVARCHAR(100),
    Фамилия1 NVARCHAR(100),
    Имя1 NVARCHAR(100),
    СерияПаспорта1 NVARCHAR(10),
    НомерПаспорта1 NVARCHAR(20),
    НомерID1 NVARCHAR(50),
    НомерТелефона1 NVARCHAR(50),
    НомерТелеграмма1 NVARCHAR(20),

    -- Вторая роль
    Статус2 NVARCHAR(100),
    Фамилия2 NVARCHAR(100),
    Имя2 NVARCHAR(100),
    СерияПаспорта2 NVARCHAR(10),
    НомерПаспорта2 NVARCHAR(20),
    НомерID2 NVARCHAR(50),
    НомерТелефона2 NVARCHAR(50),
    НомерТелеграмма2 NVARCHAR(20),

    -- Третья роль
    Статус3 NVARCHAR(100),
    Фамилия3 NVARCHAR(100),
    Имя3 NVARCHAR(100),
    СерияПаспорта3 NVARCHAR(10),
    НомерПаспорта3 NVARCHAR(20),
    НомерID3 NVARCHAR(50),
    НомерТелефона3 NVARCHAR(50),
    НомерТелеграмма3 NVARCHAR(20),

    GUID UNIQUEIDENTIFIER NOT NULL DEFAULT NEWID(),
    Рейтинг DECIMAL(5,2),
    ФИО NVARCHAR(255),
    ИД NVARCHAR(255)
)
END

    '''

    create_phones_table = '''
        IF OBJECT_ID('ТелефоныКлиентов', 'U') IS NULL
        BEGIN
            CREATE TABLE ТелефоныКлиентов (
                Код INT IDENTITY(1,1) PRIMARY KEY,
                КодКлиента INT NOT NULL,
                Телефон NVARCHAR(20),
                FOREIGN KEY (КодКлиента) REFERENCES Клиенты(КодКлиента)
            )
        END
    '''

    cursor.execute(create_clients_table)
    cursor.execute(create_phones_table)

    conn.commit()
    conn.close()

    print("Таблицы 'Клиенты' и 'ТелефоныКлиентов' созданы успешно или уже существуют.")

def Create_Scladi():
    conn = get_connection()
    cursor = conn.cursor()

    # Создание таблицы Склады
    create_scladi_table = '''
            IF OBJECT_ID('Склады', 'U') IS NULL
            BEGIN
                CREATE TABLE Склады (
                    КодСклада INT PRIMARY KEY IDENTITY(1,1),
                    GUID UNIQUEIDENTIFIER NOT NULL,
                    Наименование NVARCHAR(255) NOT NULL,
                    Адрес NVARCHAR(1000),
                    Префикс NVARCHAR(50)
                )
            END
        '''
    cursor.execute(create_scladi_table)

    conn.commit()
    conn.close()

    print("Таблицы 'Склады' создан успешно или уже существуют.")

def build_date_filter_from_period(period: list[tuple[int, int]]) -> str:
    conditions = [
        f"(YEAR(DataDobavleniya) = {year} AND MONTH(DataDobavleniya) = {month})"
        for year, month in period
    ]
    return " OR ".join(conditions)

def Tovari_v_Puti(
        kod,
        period: list[tuple[int, int]],
        statusi: str,
        output_path: str = "StatusiTovarov_report.pdf",
        top_n: int = 500,
        font_path: str = "DejaVuSans.ttf",

) -> str:
    date_filter = None
    if period is not None:
        date_filter = build_date_filter_from_period(period)

    query = f"""
        SELECT TOP {top_n}
            DataPriema AS ДатаПриёма,
            Tovar AS НомерПриёма,
            TrekKod AS НомерМеста,
            AdresMagazina AS АдресМагазина,
            NaimenovanieMagazina AS NomerMagazina,
            TelMagazina AS ТелМагазина,
            VidTovara AS ВидТовара,
            TipUpakovki AS ТипУпаковки,
            Mest AS КолвоМест,
            Ves AS Вес,
            Dlina AS Длинна,
            Shirina AS Ширина,
            Vysota AS Высота,
            Obem AS Объём,
            Summa AS Сумма,
            Statusy AS Status,
            TochkaMarshruta AS Местоположение,
            DataPribytiyaIliTekushchaya AS РасчётнаяДатаПрибытия
        FROM StatusiTovarov
        WHERE Statusy IN ({statusi}) AND CAST(KodKlienta AS INT) = {int(kod)}
    """
    if date_filter:
        query += f"\nAND ({date_filter})"

    engine = create_engine(str(config.connectinon.CONNECTION_STRING))
    df = pd.read_sql(query, engine)

    for col in ["Вес", "Объём", "Сумма", "Длинна", "Ширина", "Высота"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").round(2)
    for col in ["ДатаПриёма", "РасчётнаяДатаПрибытия"]:
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.date

    class PDF(FPDF):
        def table(self, df, widths):
            self.set_font("DejaVu", "", 6)
            for col, w in zip(df.columns, widths):
                self.cell(w, 6, str(col), 1)
            self.ln()
            self.set_font("DejaVu", "", 5.5)
            for _, row in df.iterrows():
                for val, w in zip(row, widths):
                    text = str(val)
                    if self.get_string_width(text) > w - 2:
                        while self.get_string_width(text + "...") > w - 2 and len(text) > 0:
                            text = text[:-1]
                        text += "..." if len(text) > 0 else ""
                    self.cell(w, 5, text, 1)
                self.ln()

    # Создание PDF
    pdf = PDF("L", "mm", "A4")
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Автоопределение ширины колонок
    pdf.set_font("DejaVu", "", 5.5)
    widths = [
        pdf.get_string_width(str(max([str(x) for x in df[col]] + [col], key=len))) + 4
        for col in df.columns
    ]

    # Таблица
    pdf.table(df, widths)

    # Сохранение`
    pdf.output(output_path)
    return os.path.abspath(output_path)

def MyKods(user_number: str, output_path: str = "client_table.pdf", font_path: str = "DejaVuSans.ttf",):
    conn = get_connection()
    cursor = conn.cursor()

    # Получаем список кодов клиента по номеру телефона
    cursor.execute("SELECT КодКлиента FROM ТелефоныКлиентов WHERE Телефон = ?", (user_number,))
    kodKlienta = cursor.fetchall()
    # Извлекаем коды клиента
    client_ids = [row[0] for row in kodKlienta]

    # Создаём плейсхолдеры для IN (?, ?, ...)
    placeholders = ', '.join(str(x) for x in client_ids)
    query = f"SELECT * FROM Клиенты WHERE КодКлиента IN ({placeholders})"
    engine = create_engine(str(config.connectinon.CONNECTION_STRING))
    df = pd.read_sql(query, engine)

    # Класс PDF
    class PDF(FPDF):
        def table(self, df, widths):
            self.set_font("DejaVu", "", 6)
            for col, w in zip(df.columns, widths):
                self.cell(w, 6, str(col), 1)
            self.ln()
            self.set_font("DejaVu", "", 5.5)
            for _, row in df.iterrows():
                for val, w in zip(row, widths):
                    text = str(val)
                    if self.get_string_width(text) > w - 2:
                        while self.get_string_width(text + "...") > w - 2 and len(text) > 0:
                            text = text[:-1]
                        text += "..." if len(text) > 0 else ""
                    self.cell(w, 5, text, 1)
                self.ln()

    # Создание PDF
    pdf = PDF("L", "mm", "A4")
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Автоопределение ширины колонок
    pdf.set_font("DejaVu", "", 5.5)
    widths = [
        pdf.get_string_width(str(max([str(x) for x in df[col]] + [col], key=len))) + 4
        for col in df.columns
    ]

    # Таблица
    pdf.table(df, widths)

    # Сохранение`
    pdf.output(output_path)
    return os.path.abspath(output_path)


def wrap_text(text, width=30):
    import textwrap
    if isinstance(text, str):
        return '\n'.join(textwrap.wrap(text, width=width))
    return text



def Poluchennie_tovari(output_path="Vse_tovari.pdf"):
    # Подключение к БД
    engine = create_engine(str(config.connectinon)    )

    # SQL-запрос — выбираем все поля с нужными статусами
    query = """
    SELECT *
    FROM StatusiTovarov
    WHERE Status IN (6)
    """

    # Чтение в DataFrame
    df = pd.read_sql(query, engine)

    # Преобразование и округление чисел и даты, если такие столбцы есть
    for col in ["Ves", "Obem", "Summa", "Dlina", "Shirina", "Vysota", "Cena"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").round(2)

    for col in ["DataDobavleniya", "DataPriema", "DataPribytiya", "DataPribytiyaIliTekushchaya"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.date

    # Создание фигуры
    fig, ax = plt.subplots(figsize=(22, 14))  # увеличенный размер
    ax.axis('off')

    # Создание таблицы
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc='center',
        loc='center',
        bbox=[0, 0.1, 1, 0.85]
    )

    # Настройка таблицы
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    table.scale(1, 1.1)

    # Сохраняем PDF
    plt.savefig(output_path, bbox_inches='tight')

    return os.path.abspath(output_path)

def Pribivshie_tovati(output_path="Vse_tovari.pdf"):
    # Подключение к БД
    engine = create_engine(str(config.connectinon)
    )

    # SQL-запрос — выбираем все поля с нужными статусами
    query = """
    SELECT *
    FROM StatusiTovarov
    WHERE Status IN (5)
    """

    # Чтение в DataFrame
    df = pd.read_sql(query, engine)

    # Преобразование и округление чисел и даты, если такие столбцы есть
    for col in ["Ves", "Obem", "Summa", "Dlina", "Shirina", "Vysota", "Cena"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").round(2)

    for col in ["DataDobavleniya", "DataPriema", "DataPribytiya", "DataPribytiyaIliTekushchaya"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.date

    # Создание фигуры
    fig, ax = plt.subplots(figsize=(22, 14))  # увеличенный размер
    ax.axis('off')

    # Создание таблицы
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc='center',
        loc='center',
        bbox=[0, 0.1, 1, 0.85]
    )

    # Настройка таблицы
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    table.scale(1, 1.1)

    # Сохраняем PDF
    plt.savefig(output_path, bbox_inches='tight')

    return os.path.abspath(output_path)


# Создаём товары
def fill_tovary_test_data(count=5):
    conn = get_connection()
    cursor = conn.cursor()

    for i in range(count):
        cursor.execute("INSERT INTO Tovary DEFAULT VALUES")

    conn.commit()
    conn.close()
    print(f"✅ Добавлено {count} товаров в Tovary.")

# Добавляем записи в Svedeniya_o_tovare
def fill_svedeniya_test_data(count=10):
    conn = get_connection()
    cursor = conn.cursor()

    # Получаем все TovarID из Tovary
    cursor.execute("SELECT ID FROM Tovary")
    tovar_ids = [row[0] for row in cursor.fetchall()]
    if not tovar_ids:
        raise Exception("❌ В таблице Tovary нет записей. Сначала вызови fill_tovary_test_data().")

    klienty = ["KE QIAO", "YULDA", "LI MEI", "CHINA IMPORT"]
    upakovki = ["Rulon", "Korobka", "Paleta", "Meshok"]
    vidy_tovara = ["Textile", "Plastic", "Electronics", "Material Poliester"]

    for _ in range(count):
        tovar_id = random.choice(tovar_ids)
        tip_upakovki = random.choice(upakovki)
        vid_tovara = random.choice(vidy_tovara)
        klient = random.choice(klienty)
        vsego_mest = random.randint(1, 10)
        ves = round(random.uniform(0.5, 50.0), 2)
        dlina = round(random.uniform(10.0, 150.0), 1)
        shirina = round(random.uniform(10.0, 100.0), 1)
        vysota = round(random.uniform(10.0, 100.0), 1)
        obem = round((dlina * shirina * vysota) / 1_000_000, 4)  # куб.м
        summa = round(random.uniform(100.0, 1000.0), 2)
        nomer_mesta = f"M-{random.randint(100, 999)}"
        data_dobavleniya = datetime.now() - timedelta(days=random.randint(0, 30))

        cursor.execute("""
            INSERT INTO Svedeniya_o_tovare (
                TovarID, TipUpakovki, VidTovara, Klient,
                Obem, Ves, Dlina, Shirina, Vysota,
                NomerMesta, VsegoMest,
                CenaZaKub, CenaZaTonnu, PoVesu, Summa,
                VozvratTovara, EtoPochta,
                SummaBrend, SummaZ, DataDobavleniya
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tovar_id, tip_upakovki, vid_tovara, klient,
            obem, ves, dlina, shirina, vysota,
            nomer_mesta, vsego_mest,
            None, None, None, summa,
            0, 0, None, None,
            data_dobavleniya
        ))

    conn.commit()
    conn.close()
    print(f"✅ Добавлено {count} записей в Svedeniya_o_tovare.")
    #

# Добавленые данных
def check_and_add_user(telegram_id, username, first_name, last_name, phone_number):
    conn = get_connection()
    cursor = conn.cursor()

    # Проверяем наличие по Ид (можно также по telegram_id, если хранится отдельно)
    cursor.execute("SELECT COUNT(*) FROM TelegramChats WHERE Ид = ?", telegram_id)
    exists = cursor.fetchone()[0]

    if exists == 0:
        # Находим максимальный Код
        cursor.execute("SELECT ISNULL(MAX(Код), 0) + 1 FROM TelegramChats")
        new_code = cursor.fetchone()[0]

        # Добавляем нового пользователя
        cursor.execute("""
            INSERT INTO TelegramChats (
                Код, Наименование, НомерТелефона,Родитель, ЭтоГруппа, ПометкаУдаления,
                Предопределенный, ИмяПредопределенныхДанных, Ид,
                чТип, чЗаголовок, чИнтернетИмя, чИмя, чФамилия,
                пЭтоБот, пИмя, пФамилия, пИнтернетИмя, пКодЯзыка, Ссылка
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
                       new_code, f'{first_name} {last_name}', phone_number,None, 0, 0, 0, None, telegram_id,
                       'user', None, username, first_name, last_name,
                       0, None, None, None, 'ru', None)

        conn.commit()
        result = f"✅ Новый пользователь добавлен: {first_name} {last_name} (id: {telegram_id})"
    else:
        result = f"ℹ Пользователь уже существует: {first_name} {last_name} (id: {telegram_id})"

    cursor.close()
    conn.close()
    return result

def check_Client(PhoneNumber):
    conn = get_connection()
    cursor = conn.cursor()
    result = False
    # Проверяем наличие по Ид (можно также по telegram_id, если хранится отдельно)
    cursor.execute("SELECT COUNT(*) FROM ТелефоныКлиентов WHERE Телефон = ?", PhoneNumber)
    exists = cursor.fetchone()[0]

    if exists == 0:
        result = False
    else:
        result = True

    cursor.close()
    conn.close()
    return result

def Check_lan(telegram_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Проверяем наличие записи
    cursor.execute("SELECT COUNT(*) FROM TelegramChats WHERE Ид = ?", telegram_id)
    exists = cursor.fetchone()[0]

    if exists == 0:
        result = 'ru'
    else:
        cursor.execute("SELECT пКодЯзыка FROM TelegramChats WHERE Ид = ?", telegram_id)
        row = cursor.fetchone()
        result = row[0] if row and row[0] else 'ru'

    conn.close()
    return result

def get_all_sklady():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT GUID, Наименование, Адрес FROM Склады")
    rows = cursor.fetchall()

    sklady = []
    for row in rows:
        sklady.append({
            "guid": str(row.GUID),
            "name": row.Наименование,
            "address": row.Адрес
        })

    cursor.close()
    conn.close()
    return sklady

def update_language_by_telegram_id(telegram_id, new_language_code):
    conn = get_connection()
    cursor = conn.cursor()

    # Проверяем, существует ли запись
    cursor.execute("SELECT COUNT(*) FROM TelegramChats WHERE Ид = ?", telegram_id)
    exists = cursor.fetchone()[0]

    if exists != 0:
        # Обновляем язык
        cursor.execute(
            "UPDATE TelegramChats SET пКодЯзыка = ? WHERE Ид = ?",
            new_language_code, telegram_id
        )
        conn.commit()  # не забываем сохранить изменения

    conn.close()