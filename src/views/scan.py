import flet as ft

from core.theme import PRIMARY, SURFACE_LIGHT, TEXT_SECONDARY
from core.tokens import SPACE_LG, SPACE_XL, SPACE_XXL
from core.state import state


def build_scan_view(
    page: ft.Page,
    navigate,
    ad_service,
    on_camera,
    on_gallery,
    credit_service,
) -> ft.View:
    async def show_interstitial(e):
        await ad_service.show_interstitial()

    async def open_camera(e):
        remaining = await credit_service.get_remaining()
        if remaining <= 0:
            page.show_dialog(
                ft.SnackBar(
                    content=ft.Text("Daily scans used up. Watch an ad to continue."),
                    bgcolor=ft.Colors.WARNING,
                )
            )
            return
        await ad_service.show_interstitial()
        on_camera()

    async def open_gallery(e):
        remaining = await credit_service.get_remaining()
        if remaining <= 0:
            page.show_dialog(
                ft.SnackBar(
                    content=ft.Text("Daily scans used up. Watch an ad to continue."),
                    bgcolor=ft.Colors.WARNING,
                )
            )
            return
        await ad_service.show_interstitial()
        on_gallery()

    remaining = state.scans_today

    header = ft.Container(
        content=ft.Row(
            [
                ft.Text("DocLens", size=20, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.CAMERA_ALT_OUTLINED, size=16, color=TEXT_SECONDARY),
                        ft.Text(
                            f"{remaining}/5",
                            size=14,
                            color=TEXT_SECONDARY,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.SETTINGS_OUTLINED,
                            icon_color=TEXT_SECONDARY,
                            icon_size=20,
                            on_click=lambda e: navigate("/settings"),
                        ),
                    ],
                    spacing=4,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.Padding(SPACE_XL, SPACE_LG, SPACE_XL, SPACE_LG),
    )

    camera_btn = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Icon(ft.Icons.CAMERA_ALT_ROUNDED, size=48, color=PRIMARY),
                    width=96,
                    height=96,
                    border_radius=48,
                    bgcolor=ft.Colors.with_opacity(0.1, PRIMARY),
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Container(height=SPACE_LG),
                ft.Text("Take Photo", size=18, weight=ft.FontWeight.W_600),
                ft.Text(
                    "Capture a document with your camera",
                    size=13,
                    color=TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        padding=SPACE_XXL,
        border_radius=24,
        bgcolor=SURFACE_LIGHT,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.1, PRIMARY)),
        ink=True,
        on_click=open_camera,
    )

    gallery_btn = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Icon(ft.Icons.PHOTO_LIBRARY_ROUNDED, size=48, color=PRIMARY),
                    width=96,
                    height=96,
                    border_radius=48,
                    bgcolor=ft.Colors.with_opacity(0.1, PRIMARY),
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Container(height=SPACE_LG),
                ft.Text("Choose from Gallery", size=18, weight=ft.FontWeight.W_600),
                ft.Text(
                    "Pick an existing image",
                    size=13,
                    color=TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        padding=SPACE_XXL,
        border_radius=24,
        bgcolor=SURFACE_LIGHT,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.1, PRIMARY)),
        ink=True,
        on_click=open_gallery,
    )

    content = ft.Column(
        [
            header,
            ft.Container(expand=True),
            camera_btn,
            ft.Container(height=SPACE_XL),
            gallery_btn,
            ft.Container(expand=True),
            ad_service.get_banner_ad(),
        ],
        spacing=0,
        expand=True,
    )

    return ft.View(route="/scan", controls=[content], padding=0)
