import json
import logging
import re

import requests
from bs4 import BeautifulSoup

from log_service import LogHandler
from models import Placeholder, Post
from settings import load_envs
from login_nonce import login, login_get_nonce, set_nonce_header, save_session, load_session
from text_services import get_symbols_count

logger = logging.getLogger("main")
logger.setLevel("INFO")


def get_posts_page(session: requests.Session, date: str, post_page_number: int, debug: bool):
    if debug:
        with open('posts_page_1.html', 'r', encoding="utf-8") as f:
            html_as_str = f.read()
        return html_as_str
    # Send a GET request to the posts page to get the list of posts
    response = session.get(
        f'{settings.wordpress_address}'
        f'/wp-admin/edit.php?s&post_status=all&post_type=post'
        f'&action=-1&m={date}&cat=0&paged={post_page_number}&action2=-1'
    )
    return response.text


def parse_posts_from_one_page(soup: BeautifulSoup):
    # table = soup.find('table', class_='wp-list-table')
    table_tbody = soup.find(id="the-list")

    # Find the rows in the table
    rows = table_tbody.find_all('tr')

    # Iterate over the rows and extract the posts published in December 2022
    posts = []
    for row in rows:
        title_td = row.find('td', class_='title')
        title = title_td.find('strong').string

        link = title_td.find('a')['href']

        date_td = row.find('td', class_='date')
        date_str = date_td.get_text(separator=" ")
        if isinstance(date_td, str):
            date_str = date_str.strip()

        category_td = row.find('td', class_='categories')
        category_str = category_td.get_text(separator=" ")
        if isinstance(category_str, str):
            category_str = category_str.strip()

        if isinstance(title, str):
            posts.append(Post(title.strip(), link, date_str, category_str))
    return posts


def get_total_posts_pages_count(soup: BeautifulSoup) -> int:
    total_pages_element = soup.find('span', class_='total-pages')
    try:
        return int(total_pages_element.string)
    except Exception:
        return None


def get_post_json(session: requests.Session, id: int, debug: bool) -> dict:
    if debug:
        with open('edit_page_1.html', 'r', encoding="utf-8") as f:
            html_as_str = f.read()
        return BeautifulSoup(html_as_str, 'html.parser')
    response = session.get(
        f'{settings.wordpress_address}'
        # f'/wp-admin/post.php?post={id}&action=edit'
        # f'/wp-json/wp/v2/posts/{id}?&_locale=user'
        f'/wp-json/wp/v2/posts/{id}?context=edit&_locale=user'
    )
    return json.loads(response.text)


def get_post_length(dict1: dict) -> int:
    title_str = dict1.get('title').get('rendered')
    content_str = dict1.get('content').get('rendered')
    soup_title = BeautifulSoup(title_str, 'html.parser')
    title_text = soup_title.get_text()
    # logger.info(title_text)

    soup = BeautifulSoup(content_str, 'html.parser')
    content_text = soup.get_text()
    # logger.info(content_text)
    return get_symbols_count(title_text)+get_symbols_count(content_text)


if __name__ == "__main__":
    settings = load_envs()
    logger.info("Loaded enviroments:")
    logger.info(settings)

    session = load_session()
    if session is None:
        logger.info('Произвожу вход на сайт...')
        session = requests.Session()

        if not login(session, settings.debug, settings):
            logger.error('Вход на сайт не удался! Проверьте адрес сайта, логин и пароль')
            exit()
        logger.info('Вход на сайт выполнен успешно')
        logger.info('Получение nonce кода...')
        nonce = login_get_nonce(session, settings)
        logger.info(f'nonce код получен: {nonce}')
        set_nonce_header(session, nonce)
        save_session(session)
    else:
        logger.info('Загружена сессия с диска')

    # Test editor
    edit_json = get_post_json(session, 282355, settings.debug)
    len1 = get_post_length(edit_json)
    logger.error(len1)
    exit()



    # Send a GET request to the posts page to get the list of posts
    response_text = get_posts_page(session, settings.yearmonth, 1, settings.debug)

    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response_text, 'html.parser')
    total_pages_count = get_total_posts_pages_count(soup)
    logger.info(f'Найдено страниц с постами: {total_pages_count}')
    if total_pages_count is None:
        logger.error('Не удаётся получить общее количество страниц с постом!')
        exit()

    # Find the table with the list of posts
    all_posts = []
    for current_page_number in range(1, total_pages_count+1):

        # DEBUG BREAKING
        if settings.debug and current_page_number > 3:
            logger.info('DEBUGGING BREAK')
            break
        logger.info(f'Собираю посты со страницы № {current_page_number}...')
        response_text = get_posts_page(session, settings.yearmonth, current_page_number, settings.debug)
        soup = BeautifulSoup(response_text, 'html.parser')
        posts = parse_posts_from_one_page(soup)
        all_posts.extend(posts)

    # # Print the list of posts
    for post in all_posts:
        logger.info(post)
    logger.info(f'Всего найдено постов: {len(all_posts)}')

    log_handler = LogHandler('./result_log.csv')
    log_handler.open_log()
    logger.info('Уже обработанные посты:')
    logger.info(log_handler.already_edited_posts_ids)
    for post in all_posts[:5]:
        log_handler.add_post(post)
