import threading

from app.pipeline import AltTextPipeline
from app.utils.utils import log_info_message


class PipelineFactory:
    _pipeline = None
    _lock = threading.Lock()

    @classmethod
    def get(cls):
        if cls._pipeline is None:
            with cls._lock:
                if cls._pipeline is None:
                    log_info_message(
                        "✅ Initializing pipeline and loading models"
                    )
                    cls._pipeline = AltTextPipeline()
        log_info_message("✅ Fetching already initialised pipeline and models")
        return cls._pipeline
