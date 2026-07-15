from sqlalchemy import inspect

from infrastructures.persistence.model.meta import Base
from infrastructures.persistence.model.mixin import (
    IDMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class AbstractModel(Base):
    """
    Base model with migration support.
    """

    __abstract__ = True
    __table_args__ = {"extend_existing": True}

    def __repr__(self) -> str:
        class_name = self.__class__.__name__

        state = inspect(self)
        field_strings = []
        for attr in state.mapper.column_attrs:
            field_strings.append(f"{attr.key}={getattr(self, attr.key)!r}")

        return f"{class_name}({', '.join(field_strings)})"


class PersistentModel(Base, IDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Base model with ID, timestamps, and soft delete functionality.
    """

    __abstract__ = True
    __table_args__ = {"extend_existing": True}

    def __repr__(self) -> str:
        class_name = self.__class__.__name__

        state = inspect(self)
        field_strings = []
        for attr in state.mapper.column_attrs:
            field_strings.append(f"{attr.key}={getattr(self, attr.key)!r}")

        return f"{class_name}({', '.join(field_strings)})"
