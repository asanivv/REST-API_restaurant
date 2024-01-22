from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import URL

from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_BASE


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


url_object = URL.create(
    "postgresql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    database=DB_BASE,
    port=DB_PORT,
)


# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_BASE}"

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"check_same_thread": False} # .is needed only for SQLite. It's not needed for other databases.
# )

engine = create_engine(url_object)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
