import logging

import requests
from bs4 import BeautifulSoup

from models import Post
from settings import load_envs

logger = logging.getLogger("main")
logger.setLevel("INFO")


def login(session: requests.Session, debug: bool):
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


if __name__ == "__main__":
    settings = load_envs()
    logger.info("Loaded enviroments:")
    logger.info(settings)

    session = requests.Session()

    if not login(session, settings.debug):
        logger.error('Вход на сайт не удался! Проверьте адрес сайта, логин и пароль')
        exit()
    logger.info('Вход на сайт выполнен успешно')

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
        if settings.debug and current_page_number > 3:
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
