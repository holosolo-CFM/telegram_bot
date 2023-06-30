import requests
from config_data import config
'''
Функция которая при обращении проверяет, все ли в порядке с ответом, если да то возвращает json объект
'''
def api_request(method_endswith,  # Меняется в зависимости от запроса. locations/v3/search либо properties/v2/list
                params,  # Параметры, если locations/v3/search, то {'q': 'Рига', 'locale': 'ru_RU'}
                method_type  # Метод\тип запроса GET\POST
                ):
    url = f"https://hotels4.p.rapidapi.com/{method_endswith}"
    get_headers = {
	"X-RapidAPI-Key": config.RAPID_API_KEY,
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    post_headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    # В зависимости от типа запроса вызываем соответствующую функцию
    if method_type == 'GET':
        return get_request(
            url=url,
            headers=get_headers,
            params=params
        )
    else:
        return post_request(
            url=url,
            headers=post_headers,
            params=params
        )


def get_request(url,headers,params):
    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=15
        )
        if response.status_code == requests.codes.ok:
            return response.json()
    except Exception:
        print('Ошибка в Апи гет')

def post_request(url,headers,params):
    try:
        response = requests.post(
            url,
            json=params,
            headers=headers
        )
        if response.status_code == requests.codes.ok:
            return response.json()
    except Exception:
        print('Ошибка в Апи Пост')