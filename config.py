import os

BASE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'data', 'jax.db')
PATH_DB = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')), 'static', 'data', 'jax.db')

class Config:
    SECRET_KEY = "e349a8b57ff44c3a9b7c1b2f15b03e4e"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + PATH_DB.replace('\\', '/')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
