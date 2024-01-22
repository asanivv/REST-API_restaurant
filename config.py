from dotenv import load_dotenv
import os


load_dotenv()

DB_HOST = os.environ.get("HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_USER = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_BASE = os.environ.get("DATABASE")
