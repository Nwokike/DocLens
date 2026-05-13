import flet as ft

from core.constants import DAILY_SCAN_LIMIT
from core.state import state
from core.theme import PRIMARY, TEXT_SECONDARY
from core.tokens import SPACE_LG, SPACE_XL, SPACE_XXL


def build_scan_view(
    page: ft.Page,
    navigate,
    ad_service,
    on_camera,
    on_gallery,
    credit_service,
) -> ft.View:
    async def _try_use_scan():
        remaining = await credit_service.get_remaining()
        if remaining > 0:
            return True
        ok = await ad_service.show_rewarded()
        if ok:
            return await credit_service.use_scan()
        return False

    async def _open_camera_async():
        if not await _try_use_scan():
            return
        await ad_service.show_interstitial()
        await on_camera()

    def open_camera(e):
        page.run_task(_open_camera_async)

    async def _open_gallery_async():
        if not await _try_use_scan():
            return
        await ad_service.show_interstitial()
        on_gallery()

    def open_gallery(e):
        page.run_task(_open_gallery_async)

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        state.theme_mode = page.theme_mode
        page.update()

    theme_icon = ft.Icons.DARK_MODE_ROUNDED if page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE_ROUNDED

    header = ft.Container(
        content=ft.Row(
            [
                ft.Text("DocLens", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.CAMERA_ALT_OUTLINED, size=16, color=TEXT_SECONDARY),
                        ft.Text(
                            f"{state.scans_today}/{DAILY_SCAN_LIMIT}",
                            size=14,
                            color=TEXT_SECONDARY,
                        ),
                        ft.IconButton(
                            icon=theme_icon,
                            icon_color=TEXT_SECONDARY,
                            icon_size=20,
                            on_click=toggle_theme,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.SETTINGS_OUTLINED,
                            icon_color=TEXT_SECONDARY,
                            icon_size=20,
                            on_click=lambda e: page.run_task(navigate, "/settings"),
                        ),
                    ],
                    spacing=4,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.Padding(SPACE_XL, SPACE_XL, SPACE_XL, SPACE_LG),
        margin=ft.Margin(0, 0, 0, 0),
    )

    card_padding = SPACE_XXL
    card_border = ft.Border.all(1, ft.Colors.with_opacity(0.1, PRIMARY))

    def _card(on_click):
        return ft.Container(
            content=ft.Column(
                controls=[],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            padding=card_padding,
            border_radius=24,
            bgcolor=ft.Colors.SURFACE,
            border=card_border,
            ink=True,
            on_click=on_click,
        )

    camera_btn = _card(open_camera)
    camera_btn.content.controls = [
        ft.Container(
            content=ft.Icon(ft.Icons.CAMERA_ALT_ROUNDED, size=48, color=PRIMARY),
            width=96,
            height=96,
            border_radius=48,
            bgcolor=ft.Colors.with_opacity(0.1, PRIMARY),
            alignment=ft.Alignment.CENTER,
        ),
        ft.Container(height=SPACE_LG),
        ft.Text("Take Photo", size=18, weight=ft.FontWeight.W_600, color=ft.Colors.ON_SURFACE),
        ft.Text("Capture a document with your camera", size=13, color=TEXT_SECONDARY, text_align=ft.TextAlign.CENTER),
    ]

    gallery_btn = _card(open_gallery)
    gallery_btn.content.controls = [
        ft.Container(
            content=ft.Icon(ft.Icons.PHOTO_LIBRARY_ROUNDED, size=48, color=PRIMARY),
            width=96,
            height=96,
            border_radius=48,
            bgcolor=ft.Colors.with_opacity(0.1, PRIMARY),
            alignment=ft.Alignment.CENTER,
        ),
        ft.Container(height=SPACE_LG),
        ft.Text("Choose from Gallery", size=18, weight=ft.FontWeight.W_600, color=ft.Colors.ON_SURFACE),
        ft.Text("Pick an existing image", size=13, color=TEXT_SECONDARY, text_align=ft.TextAlign.CENTER),
    ]

    content = ft.SafeArea(
        ft.Column(
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
        ),
        expand=True,
    )

    return ft.View(route="/scan", controls=[content], padding=0)
