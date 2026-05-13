"""

DocLens — AI Document Scanner + Smart Summary + Instant Translate

"""

from __future__ import annotations

import asyncio
import logging
import sys
import warnings

import flet as ft

from core.state import state
from core.theme import AppTheme
from core.utils import prepare_image_for_ai
from services.ad_service import AdService
from services.credit_service import CreditService
from services.file_picker import FilePickerService
from services.storage_service import StorageService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
for noisy in ("flet_controls", "flet_transport", "flet_web", "concurrent.futures"):
    logging.getLogger(noisy).setLevel(logging.WARNING)
warnings.filterwarnings("always")
logger = logging.getLogger("doclens")

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main(page: ft.Page):
    page.title = "DocLens"
    page.theme = AppTheme.get_light()
    page.dark_theme = AppTheme.get_dark()
    page.theme_mode = ft.ThemeMode.LIGHT
    state.theme_mode = page.theme_mode

    page.padding = 0
    page.spacing = 0

    def on_error(e):
        logger.error("Page error: %s", e.data)
        page.snack_bar = ft.SnackBar(content=ft.Text("Something went wrong."))
        page.snack_bar.open = True
        page.update()

    page.on_error = on_error

    ad_service = AdService(page)
    storage = StorageService(page)
    credit_service = CreditService(storage)

    page.run_task(ad_service.preload_interstitial)
    page.run_task(credit_service.initialize)

    pending_image = None

    async def _process_and_navigate(data, mime, filename):
        nonlocal pending_image
        ok = await credit_service.use_scan()
        if not ok:
            page.show_dialog(ft.SnackBar(content=ft.Text("Daily scan limit reached"), bgcolor=ft.Colors.WARNING))
            return
        processed = prepare_image_for_ai(data)
        state.current_image = processed
        state.current_image_mime = mime
        state.current_image_name = filename
        state.extracted_text = ""
        state.current_summary = ""
        state.current_translation = ""
        pending_image = True
        await navigate("/result")

    def on_image_captured(data, mime, filename):
        page.run_task(_process_and_navigate, data, mime, filename)

    file_picker = FilePickerService(page, on_result=on_image_captured)

    async def on_camera():
        nonlocal pending_image
        from components.camera_viewfinder import CameraViewfinder

        def handle_capture(data: bytes, mime: str, filename: str):
            on_image_captured(data, mime, filename)

        def handle_close():
            if viewfinder in page.overlay:
                page.overlay.remove(viewfinder)
                page.update()

        viewfinder = CameraViewfinder(page, handle_capture, handle_close)
        page.overlay.append(viewfinder)
        page.update()
        ok = await viewfinder.initialize()
        if not ok:
            if viewfinder in page.overlay:
                page.overlay.remove(viewfinder)
                page.update()
            page.show_dialog(ft.SnackBar(content=ft.Text("Camera not available")))

    def on_gallery():
        file_picker.pick_image()

    async def navigate(route: str):
        page.route = route
        await route_change()

    async def route_change(e=None):
        route = page.route
        page.views.clear()

        if route in ("/", "/scan"):
            from views.scan import build_scan_view

            page.views.append(build_scan_view(page, navigate, ad_service, on_camera, on_gallery, credit_service))

        elif route == "/result":
            if not state.current_image:
                await navigate("/scan")
                return
            from views.result import build_result_view

            page.views.append(build_result_view(page, navigate))

        elif route == "/summary":
            if not state.current_image:
                await navigate("/scan")
                return
            from views.summary import build_summary_view

            page.views.append(build_summary_view(page, navigate))

        elif route == "/translate":
            if not state.current_image:
                await navigate("/scan")
                return
            from views.translate import build_translate_view

            page.views.append(build_translate_view(page, navigate))

        elif route == "/settings":
            from views.settings import build_settings_view

            view = await build_settings_view(page, navigate, credit_service, ad_service)
            page.views.append(view)

        else:
            await navigate("/scan")

        page.update()

    async def view_pop(e):
        page.views.pop()
        if page.views:
            top = page.views[-1]
            page.route = top.route
        page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.route = "/scan"
    await route_change()


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
