import aiohttp

def get_authdata():
    url = "http://localhost/tgtest/getsklad"
    auth = aiohttp.BasicAuth('Администратор', '1')
    return url, auth

async def get_http_skladi():
    structure_of_authorization = get_authdata()
    url = structure_of_authorization.url
    auth = structure_of_authorization.auth

    try:
        async with aiohttp.ClientSession(auth=auth) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Ошибка запроса: {response.status}")
                data = await response.json()  # ожидаем список складов

    except Exception as e:
        print("Ошибка при получении складов:", str(e))
        data = []
    return data

async def get_http_MyCodes():
        structure_of_authorization = get_authdata()
        url = structure_of_authorization.url
        auth = structure_of_authorization.auth

        try:
            async with aiohttp.ClientSession(auth=auth) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise Exception(f"Ошибка запроса: {response.status}")
                    data = await response.json()  # ожидаем список складов

        except Exception as e:
            print("Ошибка при получении складов:", str(e))
            data = []
        return data