import os

from sqlalchemy import create_engine
from databases import Database

from models import metadata

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)

metadata.create_all(engine)
