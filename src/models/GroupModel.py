from sqlalchemy import Index, func

from src.models.DatabaseMixins import (
    HasNameAndOptionalDescription,
    HasId,
    HasCreatedAndUpdateTimestamps,
    DatabaseBaseModel,
)


class Group(
    DatabaseBaseModel,
    HasId,
    HasCreatedAndUpdateTimestamps,
    HasNameAndOptionalDescription,
):
    __tablename__ = "groups"
    Index("idx_group_name", "name", postgresql_using="gin")
    Index("idx_group_description", "description", postgresql_using="gin")
