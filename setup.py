from setuptools import setup

# read the contents of your README file
from pathlib import Path

long_description = (Path(__file__).parent / "README.md").read_text()

setup(
    name='bestchange_api',
    version='1.0.0.2',
    description='Библиотека для работы с "api" сервиса bestchange.ru',
    packages=['bestchange_api'],
    author_email='maksam07@gmail.com',
    zip_safe=False,
    long_description=long_description,
    long_description_content_type='text/markdown'
)
