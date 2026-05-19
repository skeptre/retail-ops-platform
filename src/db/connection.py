import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    url = os.getenv('DATABASE_URL')
    if not url:
        raise ValueError('DATABASE_URL not set in environment')
    return create_engine(url)
