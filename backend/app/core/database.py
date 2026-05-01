"""
Database configuration and session management.

Reads DATABASE_URL from settings/env so the same code runs on:
  - Local dev / Replit  -> sqlite+aiosqlite:///./preharvest.db (default)
                           OR Replit's built-in Postgres (auto-detected)
  - Render (production) -> postgresql+asyncpg://...
"""
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def _normalize_db_url(url: str) -> tuple[str, dict]:
    """
    Make any common Postgres URL safe for SQLAlchemy + asyncpg:
      - postgres://       -> postgresql+asyncpg://
      - postgresql://     -> postgresql+asyncpg://
      - sqlite stays the same.
      - Strip libpq-style query params asyncpg doesn't accept (sslmode, channel_binding).
        If sslmode=require/verify-* was present, return ssl=True via connect_args.
    """
    connect_args: dict = {}

    if url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://") and "+asyncpg" not in url:
        url = "postgresql+asyncpg://" + url[len("postgresql://"):]

    if url.startswith("postgresql+asyncpg://"):
        parts = urlsplit(url)
        kept = []
        needs_ssl = False
        for k, v in parse_qsl(parts.query, keep_blank_values=True):
            kl = k.lower()
            if kl == "sslmode":
                if v.lower() in ("require", "verify-ca", "verify-full"):
                    needs_ssl = True
                # drop sslmode in either case (asyncpg doesn't take it)
                continue
            if kl == "channel_binding":
                continue
            kept.append((k, v))
        url = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(kept), parts.fragment))
        if needs_ssl:
            connect_args["ssl"] = True

    return url, connect_args


DATABASE_URL, _connect_args = _normalize_db_url(settings.DATABASE_URL)
IS_SQLITE = DATABASE_URL.startswith("sqlite")

if IS_SQLITE:
    engine = create_async_engine(
        DATABASE_URL,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_async_engine(
        DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        connect_args=_connect_args,
    )

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db():
    """Dependency for getting a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Create all tables. Safe to call on every startup."""
    # Make sure every model module is imported so SQLAlchemy registers its
    # tables on Base.metadata before create_all runs.
    from app.models import user, product, order, payment, delivery, insurance  # noqa: F401

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized (%s)", "sqlite" if IS_SQLITE else "postgres")
    except Exception as e:
        logger.warning("Database initialization skipped: %s. Running without database.", e)
