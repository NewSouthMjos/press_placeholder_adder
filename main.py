import logging

import requests

import api
from log_service import LogHandler, ResultLogRow
from models import Placeholder, Post
from settings import Settings, load_envs
from login_nonce import (
    login,
    login_get_nonce,
    set_nonce_header,
    save_session,
    load_session,
)
import text_services

logger = logging.getLogger("main")
logger.setLevel("INFO")


def parse_json_post(post_json: dict) -> Post:
    return Post(
        post_json.get("id"),
        post_json.get("title").get("rendered"),
        post_json.get("date"),
        post_json.get("status"),
        post_json.get("categories"),
        post_json.get("content").get("raw"),
    )


def get_update_single_post_test(session: requests.Session, settings: Settings):

    log_handler = LogHandler('./result_log.csv')
    log_handler.open_log()
    logger.info('Уже обработанные посты:')
    logger.info(log_handler.already_edited_posts_ids)

    post_json = api.get_post(session, settings, 282355)
    post = parse_json_post(post_json)
    placeholder_handler = text_services.PlaceholderHandler()
    placeholder_handler.load_placeholders()
    edited_post, result_row = prepare_post(settings, post, placeholder_handler)

    log_handler.add_log_row(result_row)
    # update_sigle_post(session, settings, post)


def prepare_post(
    settings: Settings,
    post: Post,
    placeholder_handler: text_services.PlaceholderHandler,
) -> tuple[Post, ResultLogRow]:
    initial_syms_count_with_spaces = text_services.get_syms_count_with_spaces(
        post.content_raw
    )
    initial_syms_count_without_spaces = (
        text_services.get_syms_count_without_spaces(post.content_raw)
        + text_services.get_syms_count_without_spaces(post.title)
    )
    diff = initial_syms_count_with_spaces - initial_syms_count_without_spaces
    placeholder = placeholder_handler.select_placeholder(diff)

    # Изменение post
    post.content_raw = "\n".join((post.content_raw, placeholder.text_initial))
    finish_syms_count = (
        text_services.get_syms_count_without_spaces(post.content_raw)
        + text_services.get_syms_count_without_spaces(post.title)
    )

    result_log_row = ResultLogRow(
        post.id,
        "нет",
        post.title,
        f"https://sgpress.ru/news/{post.id}",
        post.date,
        initial_syms_count_with_spaces,
        initial_syms_count_without_spaces,
        diff,
        placeholder.symbols_count,
        finish_syms_count,
    )
    return post, result_log_row


def update_sigle_post(
    session: requests.Session, settings: Settings, post: Post
) -> ResultLogRow:
    # logger.error(post_json)
    logger.error(post)


if __name__ == "__main__":
    settings = load_envs()
    logger.info("Loaded enviroments:")
    logger.info(settings)

    session = load_session()
    if session is None:
        logger.info("Произвожу вход на сайт...")
        session = requests.Session()

        if not login(session, settings.debug, settings):
            logger.error(
                "Вход на сайт не удался! Проверьте адрес сайта, логин и пароль"
            )
            exit()
        logger.info("Вход на сайт выполнен успешно")
        logger.info("Получение nonce кода...")
        nonce = login_get_nonce(session, settings)
        logger.info(f"nonce код получен: {nonce}")
        set_nonce_header(session, nonce)
        save_session(session)
    else:
        logger.info("Загружена сессия с диска")

    get_update_single_post_test(session, settings)
