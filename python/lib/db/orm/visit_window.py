from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Mapped, Session, mapped_column
from lib.db.base import Base


class DbVisitWindow(Base):
    id                   : Mapped[int]           = mapped_column('ID', primary_key=True)
    visit_label          : Mapped[str]           = mapped_column('Visit_label')
    window_min_days      : Mapped[Optional[int]] = mapped_column('WindowMinDays')
    window_max_days      : Mapped[Optional[int]] = mapped_column('WindowMaxDays')
    optimum_min_days     : Mapped[Optional[int]] = mapped_column('WindowOptimumDays')
    optimum_max_days     : Mapped[Optional[int]] = mapped_column('WindowOptimumDays')
    window_midpoint_days : Mapped[Optional[int]] = mapped_column('WindowMidpointDays')

    @staticmethod
    def get_with_visit_label(db: Session, visit_label: str):
        """
        Get a visit window from the database using its visit lavel, or `None` if these is no such
        visit window.
        """

        query = select(DbVisitWindow).where(DbVisitWindow.visit_label == visit_label)
        return db.execute(query).scalar_one_or_none()
