from PIL import Image
import io

from core.constants import IMAGE_MAX_WIDTH, JPEG_QUALITY


def prepare_image_for_ai(image_bytes: bytes) -> bytes:
    img = Image.open(io.BytesIO(image_bytes))

    if img.mode == "RGBA":
        img = img.convert("RGB")

    img.thumbnail((IMAGE_MAX_WIDTH, IMAGE_MAX_WIDTH))

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=JPEG_QUALITY)

    return buffer.getvalue()
