import flet as ft


@ft.observable
class AppState:
    current_image: bytes | None = None
    current_image_mime: str = ""
    current_image_name: str = ""

    extracted_text: str = ""

    current_summary: str = ""
    current_translation: str = ""
    current_target_language: str = "es"

    processing_stage: str = ""
    is_processing: bool = False

    scans_today: int = 0

    theme_mode: ft.ThemeMode = ft.ThemeMode.LIGHT

    def clear_scan(self):
        self.current_image = None
        self.current_image_mime = ""
        self.current_image_name = ""
        self.extracted_text = ""
        self.current_summary = ""
        self.current_translation = ""


state = AppState()
