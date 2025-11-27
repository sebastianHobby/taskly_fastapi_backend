from pydantic import BaseModel as BaseSchemaModel
from pydantic import ConfigDict

from app.service_layer.schemas.SchemaMixins import (
    HasId,
    HasOptionalStartAndDeadlineDates,
    HasNameAndOptionalDescription,
    HasParentProjectId,
    HasTaskOrProjectStatus,
    HasCreatedAndUpdateTimestamps,
    HasProjectType,
)


class ProjectResponse(
    BaseSchemaModel,
    HasId,
    HasOptionalStartAndDeadlineDates,
    HasNameAndOptionalDescription,
    HasParentProjectId,
    HasTaskOrProjectStatus,
    HasCreatedAndUpdateTimestamps,
    HasProjectType,
):
    """Schema returned to API consumers typically via a GET
    request or returned after update a resource"""

    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(
    BaseSchemaModel,
    HasOptionalStartAndDeadlineDates,
    HasNameAndOptionalDescription,
    HasParentProjectId,
    HasTaskOrProjectStatus,
    HasProjectType,
):
    """Schema used by API consumers to create a Project"""

    model_config = ConfigDict(from_attributes=True)


class ProjectUpdate(ProjectCreate):
    # Same as project create - Only diff is end points will require ID param
    model_config = ConfigDict(from_attributes=True)


class ProjectDelete(BaseSchemaModel):
    pass
