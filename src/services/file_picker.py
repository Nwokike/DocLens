import logging
import mimetypes

import flet as ft

logger = logging.getLogger(__name__)


class FilePickerService:
    def __init__(self, page: ft.Page, on_result):
        self._page = page
        self._on_result = on_result
        self._picker = ft.FilePicker()

    def pick_image(self):
        self._page.run_task(self._run_picker)

    async def _run_picker(self):
        try:
            result = await self._picker.pick_files(
                allowed_extensions=["png", "jpg", "jpeg", "webp"],
                allow_multiple=False,
                with_data=True,
            )

            if result and len(result) > 0:
                file = result[0]
                if file.bytes:
                    mime, _ = mimetypes.guess_type(file.name)
                    if not mime:
                        ext = file.name.split(".")[-1].lower() if "." in file.name else ""
                        mime = "image/jpeg"
                        if ext == "png":
                            mime = "image/png"
                        elif ext == "webp":
                            mime = "image/webp"

                    self._on_result(file.bytes, mime, file.name)
        except Exception as e:
            logger.error("File picker failed: %s", e)
