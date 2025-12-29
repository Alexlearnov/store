from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from settings import CONFIG

engine = create_engine(CONFIG.db_url, echo=True)

SessionLocal = sessionmaker(bind=engine)


def get_db_session() -> Generator[Session, None, None]:
    """
    Зависимость для получения сессии базы данных.
    Создаёт новую сессию для каждого запроса и закрывает её после обработки.
    """
    db: Session = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
    finally:
        db.close()
