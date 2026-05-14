import flet as ft


@ft.observable
class AppState:
    current_image: bytes | None = None
    current_image_mime: str = ""
    current_image_name: str = ""

    # Batch scan support
    batch_pages: list = None  # list of {bytes, mime, name}
    is_batch_mode: bool = False

    extracted_text: str = ""

    current_summary: str = ""
    current_translation: str = ""
    current_target_language: str = "es"

    processing_stage: str = ""
    is_processing: bool = False

    scans_today: int = 0

    theme_mode: ft.ThemeMode = ft.ThemeMode.LIGHT

    def __init__(self):
        self.batch_pages = []

    def clear_scan(self):
        self.current_image = None
        self.current_image_mime = ""
        self.current_image_name = ""
        self.extracted_text = ""
        self.current_summary = ""
        self.current_translation = ""

    def start_batch(self):
        self.batch_pages = []
        self.is_batch_mode = True

    def add_page(self, data: bytes, mime: str, name: str):
        self.batch_pages.append({"bytes": data, "mime": mime, "name": name})

    def finish_batch(self):
        self.is_batch_mode = False


state = AppState()
