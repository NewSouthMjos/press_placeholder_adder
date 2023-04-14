import logging

import requests

from settings import Settings

logger = logging.getLogger("api")


# TODO: исправить. Не рабочая функция
def get_posts(session: requests.Session, settings: Settings):
    # Send a GET request to the posts page to get the list of posts
    base_url = f'{settings.wordpress_address}/wp-json/wp/v2/posts'

    # set the date range for the month
    after = f'2020-01-01T00:00:00+04:00'
    before = f'2020-01-31T00:00:00+04:00'

    # set the query parameters for the API request
    params = {
        'after': after,
        'before': before,
        'per_page': 1,  # limit the number of posts per page to 100
        'context': 'edit',
        '_locale': 'user'
    }

    all_posts = []
    page = 1

    # make requests until all posts for the month have been retrieved
    # while True:
    response = session.get(base_url, params=params)
    logger.error(response.text)
    response.raise_for_status()
    posts = response.json()

    # if not posts:  # no more posts left to retrieve
    #     break

    all_posts.extend(posts)

    # increment the page number to retrieve the next batch of posts
    page += 1

    # update the query parameters with the page number for the next request
    params['page'] = page

    return all_posts


def get_post(session: requests.Session, settings: Settings, id: int):
    # Send a GET request to the posts page to get the list of posts
    base_url = f'{settings.wordpress_address}/wp-json/wp/v2/posts/{id}'
    params = {
        'context': 'edit',
        '_locale': 'user'
    }
    response = session.get(base_url, params=params)
    response.raise_for_status()
    post = response.json()
    return post


def update_post(session: requests.Session, settings: Settings, id: int, content: str):
    base_url = f'{settings.wordpress_address}/wp-json/wp/v2/posts/{post.id}'

    response = session.post(base_url, params=params)

