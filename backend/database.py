from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite-Engine mit Datei 'database.db'
# check_same_thread=False erlaubt Zugriff aus verschiedenen Threads
engine = create_engine(
    "sqlite:///./database.db",
    connect_args={"check_same_thread": False},
)

# Declarative Base für ORM-Modelle
Base = declarative_base()

# SessionMaker für DB-Sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Abhängigkeitsfunktion für FastAPI-Routen.

    Erstellt eine Datenbank-Sitzung und gibt sie weiter. Nach Nutzung wird die
    Sitzung ordnungsgemäß geschlossen.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
