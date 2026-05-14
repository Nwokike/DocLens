import io
import logging

from core.constants import IMAGE_MAX_WIDTH, JPEG_QUALITY

logger = logging.getLogger(__name__)

try:
    from PIL import Image

    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False
    logger.warning("Pillow not available — skipping image preprocessing")


def prepare_image_for_ai(image_bytes: bytes) -> bytes:
    if not _HAS_PIL:
        return image_bytes
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode == "RGBA":
            img = img.convert("RGB")
        img.thumbnail((IMAGE_MAX_WIDTH, IMAGE_MAX_WIDTH))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=JPEG_QUALITY)
        return buffer.getvalue()
    except Exception as e:
        logger.warning("Image preprocessing failed: %s", e)
        return image_bytes
