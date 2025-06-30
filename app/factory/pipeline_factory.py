import logging

from app.pipeline import AltTextPipeline


class PipelineFactory:
    _pipeline = None

    @classmethod
    def get(cls):
        if cls._pipeline is None:
            logging.info("✅ Initializing pipeline and loading models")
            cls._pipeline = AltTextPipeline()
        return cls._pipeline
