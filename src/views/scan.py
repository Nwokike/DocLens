import flet as ft

from core.constants import DAILY_SCAN_LIMIT
from core.state import state
from core.theme import PRIMARY, TEXT_SECONDARY
from core.tokens import RADIUS_XL, RADIUS_XXL, SPACE_LG, SPACE_MD, SPACE_XL, SPACE_XXL


def build_scan_view(page, navigate, ad_service, on_camera, on_gallery, credit_service):
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

    remaining = max(0, DAILY_SCAN_LIMIT - state.scans_today)

    header = ft.Container(
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Text("DocLens", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text("AI Document Scanner", size=13, color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE)),
                    ],
                    spacing=2,
                ),
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.CAMERA_ALT_OUTLINED, size=14, color=ft.Colors.WHITE),
                                    ft.Text(
                                        f"{remaining}/{DAILY_SCAN_LIMIT}",
                                        size=13,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.W_600,
                                    ),
                                ],
                                spacing=4,
                            ),
                            padding=ft.Padding(10, 4, 10, 4),
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            border_radius=20,
                        ),
                        ft.Container(
                            content=ft.Icon(ft.Icons.SETTINGS_ROUNDED, size=20, color=ft.Colors.WHITE),
                            width=36,
                            height=36,
                            border_radius=18,
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            alignment=ft.Alignment.CENTER,
                            ink=True,
                            on_click=lambda e: page.run_task(navigate, "/settings"),
                        ),
                    ],
                    spacing=8,
                ),
            ]
        ),
        gradient=ft.LinearGradient(
            colors=["#2563EB", "#1D4ED8"], begin=ft.Alignment.TOP_LEFT, end=ft.Alignment.BOTTOM_RIGHT
        ),
        padding=ft.Padding(SPACE_XL, SPACE_XL, SPACE_XL, SPACE_XXL),
    )

    camera_btn = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Icon(ft.Icons.CAMERA_ALT_ROUNDED, size=52, color=PRIMARY),
                    width=100,
                    height=100,
                    border_radius=50,
                    bgcolor=ft.Colors.with_opacity(0.1, PRIMARY),
                    alignment=ft.Alignment.CENTER,
                    shadow=ft.BoxShadow(
                        blur_radius=20, color=ft.Colors.with_opacity(0.15, PRIMARY), offset=ft.Offset(0, 4)
                    ),
                ),
                ft.Container(height=SPACE_LG),
                ft.Text("Scan Document", size=20, weight=ft.FontWeight.W_600, color=ft.Colors.ON_SURFACE),
                ft.Text(
                    "Use your camera to capture a document",
                    size=13,
                    color=TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        padding=SPACE_XXL,
        border_radius=RADIUS_XXL,
        bgcolor=ft.Colors.SURFACE,
        ink=True,
        on_click=open_camera,
    )

    gallery_btn = ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Icon(ft.Icons.PHOTO_LIBRARY_ROUNDED, size=28, color=PRIMARY),
                    width=56,
                    height=56,
                    border_radius=28,
                    bgcolor=ft.Colors.with_opacity(0.1, PRIMARY),
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column(
                    [
                        ft.Text("Import from Gallery", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.ON_SURFACE),
                        ft.Text("Pick an existing image", size=12, color=TEXT_SECONDARY),
                    ],
                    spacing=2,
                    expand=True,
                ),
                ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, size=20, color=TEXT_SECONDARY),
            ],
            spacing=SPACE_MD,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=SPACE_LG,
        border_radius=RADIUS_XL,
        bgcolor=ft.Colors.SURFACE,
        ink=True,
        on_click=open_gallery,
    )

    return ft.View(
        route="/scan",
        controls=[
            ft.SafeArea(
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
            ),
        ],
        padding=0,
    )
