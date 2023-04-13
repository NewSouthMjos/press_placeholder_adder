import logging
from pathlib import Path
import re
import pickle
import time

import requests
from bs4 import BeautifulSoup

# from settings import load_envs

logger = logging.getLogger("main")


def login(session: requests.Session, debug: bool, settings):
    """Возвращает True при успешном логине"""
    if debug:
        return True
    # Send a GET request to the login page to get the login form
    response = session.get(f'{settings.wordpress_address}/wp-login.php')
    soup = BeautifulSoup(response.text, 'html.parser')
    inputs = soup.find_all('input', {'type': ['hidden', 'submit']})
    form_data = {}
    for i in inputs:
        if i.has_attr('name'):
            form_data[i['name']] = i['value']

    # Add the username and password to the form data
    form_data['log'] = settings.wordpress_login
    form_data['pwd'] = settings.wordpress_password
    response = session.post(f'{settings.wordpress_address}/wp-login.php', data=form_data)
    return 'wp-admin-bar' in response.text


def login_get_nonce(session: requests.Session, settings):
    # Load the page for creating a new post.
    # We're creating a new post we just need that page to fetch a valid nonce.
    wp = session.get(f'{settings.wordpress_address}/wp-admin/post-new.php')

    # Pull out of that page the nonce from
    # 'var wpApiSettings = {"root":"wp-json\/","nonce":"xxxxxxxxxx","versionString":"wp\/v2\/"};'
    wp_nonce=re.findall('var wpApiSettings = .*\;',wp.text)
    wp_nonce=re.sub('^.*\"nonce\"\:\"','',wp_nonce[0])
    wp_nonce=re.sub('\".*$','',wp_nonce)
    return wp_nonce


def set_nonce_header(session: requests.Session, nonce: str):
    session.headers.update({'x-wp-nonce': nonce})


def save_session(session: requests.Session):
    with open("session.pkl", "wb") as f:
        pickle.dump(session, f)


def load_session() -> requests.Session | None:
    file_path = Path("session.pkl")
    if not file_path.exists():
        return None
    modified_time = file_path.stat().st_mtime
    # calculate the time difference between now and the last modified time
    time_diff = time.time() - modified_time
    # if the time difference is less than an hour, return True, otherwise False
    if time_diff >= 3600:
        logger.error('Последняя сохраненная на диск сессия была обновлена'
                     f'> 3600 секунд назад ({time_diff})')
        return None

    with open("session.pkl", "rb") as f:
        session = pickle.load(f)
    return session




# if __name__ == "__main__":
#     settings = load_envs()
#     logger.info("Loaded enviroments:")
#     logger.info(settings)

#     session = requests.Session()
#     if not login(session, settings.debug):
#         logger.error('Вход на сайт не удался! Проверьте адрес сайта, логин и пароль')
#         exit()
#     logger.info('Вход на сайт выполнен успешно')

#     nonce = login_get_nonce(session)
#     logger.error(nonce)
