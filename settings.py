import logging
from pydantic import BaseSettings, Field, ValidationError, validator, root_validator


logging.basicConfig(
    format='[%(process)02d] [%(levelname)s] [%(pathname)s:%(lineno)d]: %(message)s'
)
logger = logging.getLogger('main')


class Settings(BaseSettings):
    wordpress_address: str
    wordpress_login: str
    wordpress_password: str
    year: int
    month: int
    debug: bool = Field(default=False)
    yearmonth: str = None

    @validator('wordpress_address')
    def validate_wordpress_address(cls, v: str):
        return v.rstrip('/')

    @validator('year')
    def validate_year(cls, v: int):
        if v >= 2030 or v <= 2010:
            raise ValueError('Год должен быть между 2010 и 2030')
        return v

    @validator('month')
    def validate_month(cls, v: int):
        if v > 12 or v < 0:
            raise ValueError('Месяц должен быть между 0 и 12')
        return v

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
