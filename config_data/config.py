from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str

@dataclass
class PhoneNumber:
    number: str

@dataclass
class FirstName:
    first_name: str
@dataclass
class TovariPut:
    tovari_put: str

@dataclass
class Config:
    tg_bot: TgBot
    phone: PhoneNumber
    first_name: FirstName
    tovari_put: TovariPut

def load_config(path:str | None = None) -> Config:
    env =Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')),
                  phone=PhoneNumber(number=env('PHONE_NUMBER')),
                  first_name=FirstName(first_name=env('FIRST_NAME')),
                  tovari_put=TovariPut(tovari_put=env('TOVI_PUT')),)