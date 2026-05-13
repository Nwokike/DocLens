import flet as ft

from core.theme import PRIMARY


def build_splash_view(page: ft.Page, navigate) -> ft.View:
    return ft.View(
        route="/splash",
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(
                            ft.Icons.DOCUMENT_SCANNER_ROUNDED,
                            size=80,
                            color=PRIMARY,
                        ),
                        ft.Container(height=16),
                        ft.Text(
                            "DocLens",
                            size=32,
                            weight=ft.FontWeight.BOLD,
                            color=PRIMARY,
                        ),
                        ft.Text(
                            "AI Document Scanner",
                            size=14,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        ft.Container(height=40),
                        ft.ProgressBar(
                            width=240,
                            color=PRIMARY,
                            bgcolor=ft.Colors.with_opacity(0.15, PRIMARY),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=0,
                ),
                expand=True,
                alignment=ft.Alignment.CENTER,
            )
        ],
        padding=0,
    )
