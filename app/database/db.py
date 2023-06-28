"""Setup the Database and support functions.."""
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.config.settings import get_settings

DATABASE_URL = (
    "postgresql+asyncpg://"
    f"{get_settings().db_user}:{get_settings().db_password}@"
    f"{get_settings().db_address}:{get_settings().db_port}/"
    f"{get_settings().db_name}"
)

engine = create_async_engine(DATABASE_URL, echo=False)
Base = declarative_base()
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_database():
    """Return the database connection as a Generator."""
    async with async_session() as session:
        async with session.begin():
            yield session
