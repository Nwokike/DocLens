import flet as ft

from core.tokens import SPACE_XL


class ActionButton(ft.Container):
    def __init__(self, icon: str, label: str, color: str, on_click=None):
        super().__init__(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Icon(icon, size=24, color=ft.Colors.WHITE),
                            ft.Text(label, size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.Padding(SPACE_XL, 16, SPACE_XL, 16),
            border_radius=16,
            bgcolor=color,
            ink=True,
            on_click=on_click,
            expand=True,
        )
