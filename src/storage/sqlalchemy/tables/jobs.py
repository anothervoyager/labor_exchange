from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, Boolean, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from storage.sqlalchemy.client import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, comment="Идентификатор вакансии")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), comment="Идентификатор пользователя", nullable=False)
    title: Mapped[str] = mapped_column(String, comment="Название вакансии", nullable=False)
    description: Mapped[str] = mapped_column(Text, comment="Описание вакансии", nullable=False)
    salary_from: Mapped[float] = mapped_column(comment="Минимальная зарплата", nullable=True)
    salary_to: Mapped[float] = mapped_column(comment="Максимальная зарплата", nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="Флаг активности вакансии")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, comment="Время создания вакансии")

    user: Mapped["User"] = relationship(back_populates="jobs")  # noqa
    responses: Mapped[list["Response"]] = relationship(back_populates="job")  # noqa
