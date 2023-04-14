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


def process_multiply_posts(session: requests.Session, settings: Settings):
    logger.info("Открываю log")
    log_handler = LogHandler("./result_log.csv")
    log_handler.open_log()
    logger.info("Уже обработанные посты:")
    logger.info(log_handler.already_edited_posts_ids)

    # 281935 - официальное опубликование
    # 282355 - обычная тестовая статья
    # post_json = api.get_post(session, settings, 282356)

    logger.info("Загружаю плейсхолдеры...")
    placeholder_handler = text_services.PlaceholderHandler()
    placeholder_handler.load_placeholders()
    logger.info(
        f"Загружены плейсхолдеры с количеством символов: {placeholder_handler.placeholders.keys()}"
    )

    logger.info(
        f"Загружаю посты, начиная с {settings.start_time} и заканчивая {settings.finish_time}..."
    )
    posts_json = api.get_posts(session, settings)
    logger.info(f"Загружено постов: {len(posts_json)}")
    logger.info(f"Начинаю обрабатывать посты")
    for post_json in posts_json:
        process_single_post(
            session, settings, placeholder_handler, log_handler, post_json
        )


def process_single_post(
    session: requests.Session,
    settings: Settings,
    placeholder_handler: text_services.PlaceholderHandler,
    log_handler: LogHandler,
    post_json: dict,
):
    post = Post.parse_json_post(post_json)
    edited_post, result_row = prepare_post(settings, post, placeholder_handler)

    # Проверка: статья уже была обновлена, это записано в логах
    if edited_post.id in log_handler.already_edited_posts_ids:
        logger.info(
            f"Статья id: {edited_post.id} уже была изменена (признак: это записано в log)"
        )
        return

    # Проверка: статья уже была обновлена, по наличию обновки в статье
    if "Страничка истории" in edited_post.initial_content_raw:
        logger.info(
            f"Статья id: {edited_post.id} уже была изменена (признак: наличине Страничка истории в тексте)"
        )
        result_row.was_edited = "нет"
        log_handler.add_log_row(result_row)
        return

    # Доппроверка: статья - официальное опубликование - категории 11477 и 422
    if (11477 in edited_post.categories) or (422 in edited_post.categories):
        logger.info(
            f"Статья id: {edited_post.id} является официальным публикованием. Пропускаю"
        )
        result_row.was_edited = "нет"
        log_handler.add_log_row(result_row)
        return

    # Статья слишком коротка
    if result_row.initial_syms_count_with_spaces <= 800:
        logger.info(
            f"Статья id: {edited_post.id} слишком короткая (кол-во символов: {result_row.initial_syms_count_with_spaces}). Пропускаю"
        )
        result_row.was_edited = "нет"
        log_handler.add_log_row(result_row)
        return

    if not settings.edit_posts:
        log_handler.add_log_row(result_row)
        logger.info(f"Статья id: {edited_post.id} добавлена в лог")
        # logger.info(f'----POST_ID={edited_post.id}----')
        # logger.info(f'{edited_post.result_content_raw}')
        # logger.info(f'----/POST_ID={edited_post.id}----')
        return

    post_successfully_updated = update_sigle_post(
        session, settings, edited_post
    )
    result_row.was_edited = "да" if post_successfully_updated else "нет"
    logger.info(
        f"Статья id: {edited_post.id} обновление успешно: {result_row.was_edited}, добавлено символов: {result_row.added_syms_count}"
    )
    log_handler.add_log_row(result_row)


def prepare_post(
    settings: Settings,
    post: Post,
    placeholder_handler: text_services.PlaceholderHandler,
) -> tuple[Post, ResultLogRow]:
    initial_syms_count_with_spaces = text_services.get_syms_count_with_spaces(
        post.initial_content_raw
    )
    initial_syms_count_without_spaces = (
        text_services.get_syms_count_without_spaces(post.initial_content_raw)
        + text_services.get_syms_count_without_spaces(post.title)
    )
    diff = initial_syms_count_with_spaces - initial_syms_count_without_spaces
    placeholder = placeholder_handler.select_placeholder(diff)

    # Изменение post
    post.result_content_raw = "\n".join(
        (post.initial_content_raw, placeholder.text)
    )
    finish_syms_count = text_services.get_syms_count_without_spaces(
        post.result_content_raw
    ) + text_services.get_syms_count_without_spaces(post.title)

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
    session: requests.Session,
    settings: Settings,
    post: Post,
) -> bool:
    try:
        api.update_post(session, settings, post.id, post.result_content_raw)
        return True
    except Exception:
        logger.exception(f"Ошибка при обновлении поста {post.id=}")
    return False


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

    if settings.edit_posts:
        logger.info('ВНИМАНИЕ! Вы собираетесь ДОБАВЛЯТЬ информацию в посты, '
                    f'начиная с {settings.start_time} и заканчивая {settings.finish_time}.'
                    'Это необратимая операция. Чтобы продолжить, введите "Y"')
        user_answer = input()
        if user_answer != 'Y':
            logger.info('Карты в пас - деньги спас.')
            exit()

    process_multiply_posts(session, settings)
