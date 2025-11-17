from pydantic import BaseModel


class ApiBaseSchema(BaseModel):
    "Generic model all our schema inherit from. Allows  future global schema changes."

    pass
