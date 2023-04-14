import logging
from datetime import datetime

from pydantic import BaseSettings, Field, ValidationError, validator, root_validator
from pydantic.datetime_parse import parse_datetime
from pydantic.errors import DateTimeError


logging.basicConfig(
    format='[%(process)02d] [%(levelname)s] [%(pathname)s:%(lineno)d]: %(message)s'
)
logger = logging.getLogger('main')


class Settings(BaseSettings):
    wordpress_address: str
    wordpress_login: str
    wordpress_password: str
    start_time: str
    finish_time: str
    edit_posts: bool
    debug: bool = Field(default=False)
    yearmonth: str = None

    @validator('wordpress_address')
    def validate_wordpress_address(cls, v: str):
        return v.rstrip('/')

    @validator('start_time', 'finish_time')
    def validate_time(cls, v: str):
        try:
            parse_datetime(v)
            return v
        except DateTimeError:
            raise ValueError('Проверьте формат времени. Пример формата: 2020-01-01T00:00:00+04:00')

    @root_validator
    def concat_year_month(cls, values):
        month = str(values.get('month')).zfill(2)
        year = str(values.get('year'))
        result = year + month
        values['yearmonth'] = result
        return values


def load_envs() -> Settings:
    try:
        return Settings(_env_file='.env', _env_file_encoding='utf-8')
    except ValidationError as e:
        logger.error('FAULT WHILE LOADING EVNS:')
        raise e
