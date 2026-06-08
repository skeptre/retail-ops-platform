import os
import sqlalchemy
import dotenv

dotenv.load_dotenv()

def get_engine():
    url = os.getenv('DATABASE_URL')
    if not url:
        raise ValueError("DATABASE_URL not set in environment")
    return sqlalchemy.create_engine(url)