from fastapi import HTTPException
from starlette.requests import Request

from src.main import app
from src.repositories.DatabaseRepository import DataModelNotFound, DataModelIntegrityConflictException

# Todo could just do something simple like below - in routes UtIL
# Class ErrorHandler ()
# #   staticMethod
#     def handle_error_in_routing(exc : Exception) -> HTTPException:
#         if exs is instance (ErrorName)
#             raise HTTPException(status_code=XXX , details = some text or json
#

# Alternative is below - harder to see what is going on

""" This allows us to define in one spot how unhandled exceptions (errors) are returned to 
the client via presentation/API layer.
It also lets us process handled exceptions e.g. add a logging step"""

@app.exception_handler(DataModelNotFound)
def handle_data_error(request: Request, exc: DataModelNotFound):
    raise HTTPException(status_code=404, detail="Data not found - MAGIC HANDLER")

@app.exception_handler(DataModelIntegrityConflictException):
def handle_data_model_conflict(request: Request, exc: DataModelIntegrityConflictException):
    raise HTTPException(status_code=409, detail="Invalid state - check parent_id exists - MAGIC HANDLER" )