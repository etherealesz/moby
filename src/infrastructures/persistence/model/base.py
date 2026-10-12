from sqlalchemy import inspect

from infrastructures.persistence.model.meta import Base


class AbstractModel(Base):
    __abstract__ = True
    __table_args__ = {"extend_existing": True}

    def __repr__(self) -> str:
        class_name = self.__class__.__name__

        state = inspect(self)
        field_strings = []
        for attr in state.mapper.column_attrs:
            field_strings.append(f"{attr.key}={getattr(self, attr.key)!r}")

        return f"{class_name}({', '.join(field_strings)})"
