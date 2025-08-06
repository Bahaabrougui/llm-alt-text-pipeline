import azure.functions as func
from app.utils.globals import app
from app.factory.pipeline_factory import PipelineFactory
from app.utils.utils import save_to_db, log_info_message


@app.blob_trigger(
    arg_name="myblob",
    path="data/images/{image}",
    connection="BlobStorageConnectionString",
)
def main(myblob: func.InputStream):
    log_info_message(f"Processing blob: {myblob.name} ({myblob.length} bytes)")
    pipe = PipelineFactory.get()
    extension = myblob.name.split('.')[-1].lower()
    files = {"file": (myblob.name, myblob.read(), f"image/{extension}")}
    result = pipe.process_image(files=files)
    log_info_message(
        f"Result: {result['captions']} | Safety: {result['safety']}"
    )

    save_to_db(myblob.name, result)
