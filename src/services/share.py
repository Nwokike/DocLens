import logging
import os
from fpdf2 import FPDF

import flet as ft

logger = logging.getLogger(__name__)


class ShareService:
    def __init__(self, page: ft.Page):
        self._page = page

    async def copy_text(self, text: str):
        await self._page.clipboard.set(text)
        self._page.show_dialog(
            ft.SnackBar(content=ft.Text("Copied to clipboard"), duration=1500)
        )

    def share_text(self, text: str):
        try:
            self._page.launch_url(f"https://wa.me/?text={text[:500]}")
        except Exception:
            pass

    async def save_as_pdf(self, image_bytes: bytes, title: str = "Document") -> str | None:
        try:
            downloads = os.path.expanduser("~/Downloads")
            os.makedirs(downloads, exist_ok=True)
            path = os.path.join(downloads, f"{title}.pdf")

            pdf = FPDF()
            pdf.add_page()
            pdf.image(image_bytes, x=10, y=10, w=190)

            from PIL import Image
            import io as _io

            img = Image.open(_io.BytesIO(image_bytes))
            img_w, img_h = img.size
            aspect = img_h / img_w
            pdf_w = 190
            pdf_h = pdf_w * aspect

            if pdf_h > 270:
                pdf_h = 270

            pdf = FPDF()
            pdf.add_page()
            pdf.image(image_bytes, x=10, y=10, w=pdf_w, h=pdf_h)
            pdf.output(path)

            self._page.show_dialog(
                ft.SnackBar(content=ft.Text(f"Saved to Downloads/{title}.pdf"), duration=3000)
            )
            return path
        except Exception as e:
            logger.error("PDF save failed: %s", e)
            self._page.show_dialog(
                ft.SnackBar(content=ft.Text(f"Save failed: {e}"), bgcolor=ft.Colors.ERROR)
            )
            return None

    async def save_as_document(self, text: str, title: str = "Document") -> str | None:
        try:
            downloads = os.path.expanduser("~/Downloads")
            os.makedirs(downloads, exist_ok=True)
            path = os.path.join(downloads, f"{title}.txt")

            with open(path, "w", encoding="utf-8") as f:
                f.write(text)

            self._page.show_dialog(
                ft.SnackBar(content=ft.Text(f"Saved to Downloads/{title}.txt"), duration=3000)
            )
            return path
        except Exception as e:
            logger.error("Document save failed: %s", e)
            return None
