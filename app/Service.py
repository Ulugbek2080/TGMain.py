from fastapi import FastAPI
from pydantic import BaseModel, validator
from typing import List, Optional, Union
from datetime import datetime
import pyodbc

app = FastAPI()

# Модель склада
class Sklad(BaseModel):
    Sklad: str
    adres: str
    Префикс: str
    Guid: str

class TelegramChats(BaseModel):
    Код: str
    Наименование: str
    Родитель: str
    ЭтоГруппа: str
    ПометкаУдаления: str
    Предопределенный: str
    ИмяПредопределенныхДанных: str
    Ид: str
    чТип: str
    чЗаголовок: str
    чИнтернетИмя: str
    чИмя: str
    чФамилия: str
    пЭтоБот: str
    пИмя: str
    пФамилия: str
    пИнтернетИмя: str
    пКодЯзыка: str
    Ссылка: str
class TovarInfo(BaseModel):
    TrekKod: str                         # обязательное
    Klient: Union[str, int]             # обязательное
    Statusy: Union[str, int]            # обязательное

    NomerOrdera: Optional[Union[str, int]] = None
    KodKlienta: Optional[Union[str, int]] = None
    TipUpakovki: Optional[str] = None
    Mest: Optional[int] = None
    DataPriema: Optional[datetime] = None
    SkladPriema: Optional[str] = None
    VidTovara: Optional[str] = None
    AdresMagazina: Optional[str] = None
    TelMagazina: Optional[str] = None
    NaimenovanieMagazina: Optional[str] = None
    Dlina: Optional[float] = None
    Shirina: Optional[float] = None
    Vysota: Optional[float] = None
    Tovar: Optional[Union[str, int]] = None
    DneyVPuti: Optional[int] = None
    DataPribytiyaIliTekushchaya: Optional[datetime] = None
    Obem: Optional[float] = None
    Ves: Optional[float] = None
    Cena: Optional[float] = None
    Status: Optional[Union[str, int]] = None
    TochkaMarshruta: Optional[str] = None
    Kommentariy: Optional[str] = None
    DataPribytiya: Optional[datetime] = None
    Summa: Optional[float] = None
    Sklad: Optional[str] = None

    @validator("DataPribytiya", "DataPribytiyaIliTekushchaya", "DataPriema", pre=True)
    def empty_string_to_none(cls, v):
        return None if v == "" else v

# Подключение к SQL Server
def get_connection():
    conn_str = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=Python_base_tg;'
        'UID=sa;'
        'PWD=1212'
    )
    return pyodbc.connect(conn_str)

# POST-метод для приёма и записи складов
@app.post("/SKLADI")
def insert_sklady(sklady: List[Sklad]):
    conn = get_connection()
    cursor = conn.cursor()

    for sklad in sklady:
        cursor.execute('''
            IF EXISTS (SELECT 1 FROM Склады WHERE GUID = ?)
            BEGIN
                UPDATE Склады
                SET Наименование = ?, Адрес = ?, Префикс = ?
                WHERE GUID = ?
            END
            ELSE
            BEGIN
                INSERT INTO Склады (GUID, Наименование, Адрес, Префикс)
                VALUES (?, ?, ?, ?)
            END
        ''',
                       sklad.Guid,  # Для EXISTS
                       sklad.Sklad, sklad.adres, sklad.Префикс, sklad.Guid,  # Для UPDATE
                       sklad.Guid, sklad.Sklad, sklad.adres, sklad.Префикс  # Для INSERT
                       )

    conn.commit()
    conn.close()

    return {"status": "успешно добавлено", "кол-во": len(sklady)}

@app.post("/Svedeniya_o_tovare")
def insert_or_update_tovar(data: List[TovarInfo]):
    conn = get_connection()
    cursor = conn.cursor()

    for item in data:
        # Проверка, есть ли запись по Tovar
        cursor.execute('''
            SELECT Status FROM StatusiTovarov WHERE Tovar = ?
        ''', item.Tovar)
        result = cursor.fetchone()

        if result:
            # Сравнение статуса
            old_status = result[0]
            if old_status != item.Status:
                # Обновляем всю строку
                cursor.execute('''
                    UPDATE StatusiTovarov
                    SET Klient = ?, Statusy = ?, NomerOrdera = ?, KodKlienta = ?, TipUpakovki = ?,
                        Mest = ?, DataPriema = ?, SkladPriema = ?, VidTovara = ?, AdresMagazina = ?,
                        TrekKod = ?, TelMagazina = ?, NaimenovanieMagazina = ?, Dlina = ?, Shirina = ?, Vysota = ?,
                        DneyVPuti = ?, DataPribytiyaIliTekushchaya = ?, Obem = ?, Ves = ?, Cena = ?,
                        Status = ?, TochkaMarshruta = ?, Kommentariy = ?, DataPribytiya = ?, Summa = ?, Sklad = ?
                    WHERE Tovar = ?
                ''', item.Klient, item.Statusy, item.NomerOrdera, item.KodKlienta, item.TipUpakovki,
                               item.Mest, item.DataPriema, item.SkladPriema, item.VidTovara, item.AdresMagazina,
                               item.TrekKod, item.TelMagazina, item.NaimenovanieMagazina, item.Dlina, item.Shirina,
                               item.Vysota,
                               item.DneyVPuti, item.DataPribytiyaIliTekushchaya, item.Obem, item.Ves, item.Cena,
                               item.Status, item.TochkaMarshruta, item.Kommentariy, item.DataPribytiya, item.Summa,
                               item.Sklad,
                               item.Tovar)
        else:
            # Вставка новой записи
            cursor.execute('''
                INSERT INTO StatusiTovarov (
                    Klient, Statusy, NomerOrdera, KodKlienta, TipUpakovki,
                    Mest, DataPriema, SkladPriema, VidTovara, AdresMagazina,
                    TrekKod, TelMagazina, NaimenovanieMagazina, Dlina, Shirina, Vysota,
                    Tovar, DneyVPuti, DataPribytiyaIliTekushchaya, Obem, Ves, Cena,
                    Status, TochkaMarshruta, Kommentariy, DataPribytiya, Summa, Sklad
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', item.Klient, item.Statusy, item.NomerOrdera, item.KodKlienta, item.TipUpakovki,
                           item.Mest, item.DataPriema, item.SkladPriema, item.VidTovara, item.AdresMagazina,
                           item.TrekKod, item.TelMagazina, item.NaimenovanieMagazina, item.Dlina, item.Shirina,
                           item.Vysota,
                           item.Tovar, item.DneyVPuti, item.DataPribytiyaIliTekushchaya, item.Obem, item.Ves, item.Cena,
                           item.Status, item.TochkaMarshruta, item.Kommentariy, item.DataPribytiya, item.Summa,
                           item.Sklad)

    conn.commit()
    conn.close()

    return {"status": "успешно обработано", "кол-во": len(data)}

@app.post("/TelegramChats")
def insert_or_update_telegram_chats(data: List[TelegramChats]):
    conn = get_connection()
    cursor = conn.cursor()
    for item in data:
        # Проверка существования записи по Ид
        cursor.execute("SELECT Код FROM TelegramChats WHERE Ид = ?", item.Ид)
        exists = cursor.fetchone()

        values = (
            item.Код, item.Наименование, item.Родитель, item.ЭтоГруппа, item.ПометкаУдаления,
            item.Предопределенный, item.ИмяПредопределенныхДанных, item.Ид, item.чТип, item.чЗаголовок,
            item.чИнтернетИмя, item.чИмя, item.чФамилия, item.пЭтоБот, item.пИмя, item.пФамилия,
            item.пИнтернетИмя, item.пКодЯзыка, item.Ссылка
        )

        if exists:
            # Обновляем запись
            cursor.execute("""
                           UPDATE TelegramChats
                           SET Код= ?,Наименование = ?,Родитель= ?,ЭтоГруппа = ?, ПометкаУдаления = ?,
                               Предопределенный=?,ИмяПредопределенныхДанных = ?,чТип = ?,чЗаголовок = ?,чИнтернетИмя = ?,
                               чИмя = ?,чФамилия = ?,пЭтоБот = ?, пИмя = ?, пФамилия = ?, пИнтернетИмя = ?, пКодЯзыка = ?,
                               Ссылка  = ?
                           WHERE Ид = ?
                           """, values[:7] + values[8:])  # Пропускаем Ид в SET, но используем в WHERE
        else:
            # Вставка новой записи
            cursor.execute("""
                           INSERT INTO TelegramChats (Код, Наименование, Родитель, ЭтоГруппа, ПометкаУдаления,
                                                      Предопределенный, ИмяПредопределенныхДанных, Ид, чТип, чЗаголовок,
                                                      чИнтернетИмя, чИмя, чФамилия, пЭтоБот, пИмя, пФамилия,
                                                      пИнтернетИмя, пКодЯзыка, Ссылка)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                           """, values)

    conn.commit()
    conn.close()

    return {"status": "успешно обработано", "кол-во": len(data)}


@app.get("/")
def read_root():
    return {"message": "Привет, это мой HTTP-сервис на FastAPI!"}

