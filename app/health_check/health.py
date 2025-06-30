import azure.functions as func

from app.utils.globals import app


@app.function_name(name="health")
# Will be accessible at /api/health
@app.route(route="health")
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("OK", status_code=200)