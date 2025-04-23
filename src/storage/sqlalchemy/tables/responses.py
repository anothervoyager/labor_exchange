from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from storage.sqlalchemy.client import Base


class Response(Base):
    __tablename__ = "responses"

    # id: Mapped[int] = mapped_column(primary_key=True, comment="Идентификатор отклика")
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="Идентификатор отклика")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), comment="Идентификатор пользователя", nullable=False)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), comment="Идентификатор вакансии", nullable=False)
    message: Mapped[str] = mapped_column(Text, comment="Сообщение отклика", nullable=False)

    user: Mapped["User"] = relationship(back_populates="responses")  # noqa
    job: Mapped["Job"] = relationship(back_populates="responses")  # noqa
