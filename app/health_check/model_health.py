import azure.functions as func

from app.factory.image_captioner_factory import ImageCaptionerFactory
from app.utils.globals import app


@app.function_name(name="model_health")
# Will be accessible at /api/health
@app.route(route="model-health")
def model_health_check(req: func.HttpRequest) -> func.HttpResponse:
    image_captioner = ImageCaptionerFactory.get()
    test_image_path = ("https://huggingface.co/datasets/"
                       "Narsil/image_dummy/raw/main/lena.png")
    english_caption = image_captioner.generate_caption(
        test_image_path,
        is_url=True,
    )
    return func.HttpResponse(f"Caption is: {english_caption}", status_code=200)
