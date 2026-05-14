"""Image preprocessing - Pillow is optional. Without it, raw bytes pass through."""

import io
import logging

from core.constants import IMAGE_MAX_WIDTH, JPEG_QUALITY

logger = logging.getLogger(__name__)

try:
    from PIL import Image

    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False
    logger.info("Pillow not available - image preprocessing disabled")


def prepare_image_for_ai(image_bytes: bytes) -> bytes:
    if not _HAS_PIL:
        return image_bytes
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode == "RGBA":
            img = img.convert("RGB")
        img.thumbnail((IMAGE_MAX_WIDTH, IMAGE_MAX_WIDTH))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=JPEG_QUALITY)
        return buf.getvalue()
    except Exception as e:
        logger.warning("Image resize failed: %s", e)
        return image_bytes
