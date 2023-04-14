import logging

import requests

from settings import Settings

logger = logging.getLogger("main")


def get_posts(session: requests.Session, settings: Settings):
    # Send a GET request to the posts page to get the list of posts
    base_url = f'{settings.wordpress_address}/wp-json/wp/v2/posts'

    # set the date range for the month
    after = settings.start_time
    before = settings.finish_time

    # set the query parameters for the API request
    per_page = 100
    params = {
        'after': after,
        'before': before,
        'per_page': per_page,
        'context': 'edit',
        '_locale': 'user',
        'order': 'asc',
    }

    all_posts = []
    offset = 0

    # make requests until all posts for the month have been retrieved
    while True:
        response = session.get(base_url, params=params)
        response.raise_for_status()
        posts = response.json()

        if not posts:  # no more posts left to retrieve
            break

        all_posts.extend(posts)
        logger.info(f'{len(all_posts)}...')

        # increment the page number to retrieve the next batch of posts
        offset += per_page

        # update the query parameters with the page number for the next request
        params['offset'] = offset

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
    base_url = f'{settings.wordpress_address}/wp-json/wp/v2/posts/{id}'
    body = {'content': content}
    response = session.post(base_url, data=body)
    if not response.ok:
        raise Exception(f'Ответ сервера был: {response.status_code}')
