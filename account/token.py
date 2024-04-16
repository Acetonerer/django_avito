import requests


def get_new_access_token(client_id, client_secret):
    """
    Метод получения токена доступа Avito
    """
    url = "https://api.avito.ru/token/"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            access_token = response.json().get("access_token")
            return access_token, None
        else:
            return None, f"Error: Unable to retrieve access token. Status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return None, f"An error occurred: {e}"


def get_access_token(client_id, client_secret):
    """
    Метод получения токена доступа Avito
    """
    url = "https://api.avito.ru/token/"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            access_token = response.json().get("access_token")
            return access_token, None
        else:
            return None, f"Error: Unable to retrieve access token. Status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return None, f"An error occurred: {e}"

