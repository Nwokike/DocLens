import base64

import flet as ft

from core.theme import PRIMARY


class MediaPreview(ft.Container):
    def __init__(self, image_bytes: bytes, mime_type: str = "image/jpeg", on_clear=None):
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        self._clear_btn = ft.IconButton(
            icon=ft.Icons.CLOSE_ROUNDED,
            icon_size=16,
            width=28,
            height=28,
            style=ft.ButtonStyle(padding=0),
            on_click=lambda e: on_clear() if on_clear else None,
        )
        super().__init__(
            content=ft.Stack(
                [
                    ft.Container(
                        content=ft.Image(src=f"data:{mime_type};base64,{b64}", fit=ft.BoxFit.CONTAIN),
                        border_radius=12,
                        height=200,
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    ),
                    ft.Container(content=self._clear_btn, top=4, right=4),
                ]
            ),
            border_radius=12,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.15, PRIMARY)),
            margin=ft.Margin.symmetric(vertical=8),
        )
