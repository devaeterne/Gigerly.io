# api/app/models/base.py
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import Column, Integer, DateTime, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.inspection import inspect

# ---------- Alembic için stabil isimlendirme ----------
NAMING_CONVENTION = {
    "ix":  "ix_%(table_name)s_%(column_0_N_name)s",
    "uq":  "uq_%(table_name)s_%(column_0_N_name)s",
    "ck":  "ck_%(table_name)s_%(constraint_name)s",
    "fk":  "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
    "pk":  "pk_%(table_name)s",
}

metadata = sa.MetaData(naming_convention=NAMING_CONVENTION)

# Projedeki tüm modeller bu Base'i kullanmalı
Base = declarative_base(metadata=metadata)

# ---------- Ortak mixin'ler ----------
class IDMixin:
    """Tüm tablolarda integer auto-increment id kullanımı."""
    id = Column(Integer, primary_key=True)

class TimestampMixin:
    """
    created_at / updated_at alanları.
    Alembic migration'ında trigger ile updated_at set ediyorsan,
    buradaki server_onupdate kullanımıyla da uyumludur.
    """
    created_at = Column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=text("now()"),
        server_onupdate=text("now()"),  # trigger varsa da sorun olmaz
        nullable=False,
    )

class ReprMixin:
    """Kolay debug için sade __repr__."""
    def __repr__(self) -> str:  # pragma: no cover
        cls = self.__class__.__name__
        pk = getattr(self, "id", None)
        return f"<{cls} id={pk!r}>"

class SerializeMixin:
    """
    Basit serialize/to_dict. İlişki alanlarını derine gitmeden atlar.
    İhtiyaca göre genişletebilirsin.
    """
    def to_dict(self, *, include: set[str] | None = None, exclude: set[str] | None = None) -> dict:
        mapper = inspect(self).mapper
        data = {}
        for col in mapper.columns:
            name = col.key
            if include and name not in include:
                continue
            if exclude and name in exclude:
                continue
            data[name] = getattr(self, name)
        return data
