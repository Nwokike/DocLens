import flet as ft

from core.theme import PRIMARY
from core.tokens import SPACE_LG, SPACE_MD, SPACE_XL


def glass_card(content, width=None, padding=SPACE_XL):
    return ft.Container(
        content=content,
        width=width,
        padding=padding,
        border_radius=24,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
    )


def section_header(title):
    return ft.Container(
        content=ft.Text(title, size=12, weight=ft.FontWeight.BOLD, color=PRIMARY),
        padding=ft.Padding.only(left=SPACE_LG, top=SPACE_XL, bottom=SPACE_MD),
    )


def setting_tile(icon, title, subtitle="", trailing=None):
    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(icon, size=20, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Column(
                    [
                        ft.Text(title, size=15),
                        ft.Text(subtitle, size=12, color=ft.Colors.ON_SURFACE_VARIANT) if subtitle else ft.Container(),
                    ],
                    spacing=2,
                    expand=True,
                ),
                trailing or ft.Container(),
            ],
            spacing=SPACE_LG,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=SPACE_LG, vertical=14),
    )
