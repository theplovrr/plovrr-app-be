from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import Config

config = Config()
user = config.get("Settings.Database.User")
password = config.get("Settings.Database.Password")
host = config.get("Settings.Database.Host")
port = config.get("Settings.Database.Port")
databaseName = config.get("Settings.Database.DatabaseName")

DATABASE_URL = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{databaseName}"

# Create Async Engine & Session
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Base Model
Base = declarative_base()

# Dependency to get DB session
async def get_db():
    async with SessionLocal() as session:
        yield session
