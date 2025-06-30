import logging
import os
import azure.functions as func
from app.utils.globals import app
from app.factory.pipeline_factory import PipelineFactory
from app.utils.utils import save_to_db


@app.blob_trigger(
    arg_name="myblob",
    path="data/images/{image}",
    connection="BlobStorageConnectionString",
)
def main(myblob: func.InputStream):
    logging.info(f"Processing blob: {myblob.name} ({myblob.length} bytes)")
    local_path = f"/tmp/{os.path.basename(myblob.name)}"
    with open(local_path, "wb") as fp:
        fp.write(myblob.read())

    pipe = PipelineFactory.get()
    result = pipe.process_image(local_path)
    logging.info(f"Result: {result['captions']} | Safety: {result['safety']}")

    save_to_db(myblob.name, result)
