import logging
import azure.functions as func
import sys
import os

# Add the parent directory to sys.path to allow imports from Shared
# This is sometimes needed depending on how the Python worker handles paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Shared import db_manager

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        response_message = f"Hello, {name}."
        
        # --- Database Interaction Demo ---
        # logic: We want to store this interaction in the DB.
        try:
            # Note: This will fail if SqlConnectionString is not valid in local.settings.json
            db_manager.execute_query("INSERT INTO AccessLogs ([User], Timestamp) VALUES (?, GETDATE())", [name])
            response_message += " (DB interaction successful)"
        except Exception as e:
            logging.error(f"DB Error: {e}")
            # We don't fail the request for this demo, but we log the error
            response_message += f" (DB Error: {str(e)})"
        
        return func.HttpResponse(response_message)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
