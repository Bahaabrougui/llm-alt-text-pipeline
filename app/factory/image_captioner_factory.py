import threading

from app.captioning import ImageCaptioner
from app.utils.utils import log_info_message


class ImageCaptionerFactory:
    _image_captioner = None
    _lock = threading.Lock()

    @classmethod
    def get(cls):
        if cls._image_captioner is None:
            with cls._lock:
                if cls._image_captioner is None:
                    log_info_message(
                        "✅ Initializing Image Captioning model"
                    )
                    cls._image_captioner = ImageCaptioner()
        log_info_message(
            "✅ Fetching already initialised Image Captioning model"
        )
        return cls._image_captioner
