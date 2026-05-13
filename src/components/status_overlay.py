import flet as ft

from core.theme import PRIMARY, TEXT_SECONDARY
from core.tokens import SPACE_MD


class StatusOverlay(ft.Container):
    def __init__(self):
        self._progress = ft.ProgressRing(width=24, height=24, stroke_width=2, color=PRIMARY)
        self._status = ft.Text("", size=14, color=TEXT_SECONDARY, text_align=ft.TextAlign.CENTER)
        self._detail = ft.Text(
            "",
            size=12,
            color=ft.Colors.with_opacity(0.7, TEXT_SECONDARY),
            text_align=ft.TextAlign.CENTER,
            visible=False,
        )

        super().__init__(
            content=ft.Column(
                [self._progress, ft.Container(height=SPACE_MD), self._status, ft.Container(height=4), self._detail],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            alignment=ft.Alignment.CENTER,
            expand=True,
        )

    def set_stage(self, stage: str, detail: str = ""):
        self._status.value = stage
        if detail:
            self._detail.value = detail
            self._detail.visible = True
        self.update()

    def done(self):
        self.visible = False
        self.update()
