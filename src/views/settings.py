import flet as ft

from core.state import state
from core.theme import PRIMARY, TEXT_SECONDARY
from core.tokens import SPACE_LG, SPACE_MD, SPACE_XL
from core.constants import DAILY_SCAN_LIMIT


async def build_settings_view(page: ft.Page, navigate, credit_service, ad_service) -> ft.View:
    remaining = await credit_service.get_remaining()

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        state.theme_mode = page.theme_mode
        page.update()

    def section_header(title: str) -> ft.Container:
        return ft.Container(
            content=ft.Text(title, size=12, weight=ft.FontWeight.BOLD, color=PRIMARY),
            padding=ft.Padding.only(left=SPACE_LG, top=SPACE_XL, bottom=SPACE_MD),
        )

    def setting_tile(icon, title, subtitle="", trailing=None):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, size=20, color=TEXT_SECONDARY),
                    ft.Column(
                        [
                            ft.Text(title, size=15),
                            ft.Text(subtitle, size=12, color=TEXT_SECONDARY) if subtitle else ft.Container(),
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

    theme_icon = ft.Icons.DARK_MODE_ROUNDED if page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE_ROUNDED
    current_theme = "Dark" if page.theme_mode == ft.ThemeMode.DARK else "Light"

    controls = [
        section_header("SCANNING"),
        setting_tile(
            ft.Icons.CAMERA_ALT_OUTLINED,
            "Today's Scans",
            f"{remaining} of {DAILY_SCAN_LIMIT} remaining",
            trailing=ft.Container(
                content=ft.ProgressBar(
                    width=100,
                    value=1 - (remaining / DAILY_SCAN_LIMIT),
                    color=PRIMARY,
                    bgcolor=ft.Colors.with_opacity(0.15, PRIMARY),
                ),
            ),
        ),
        section_header("APPEARANCE"),
        setting_tile(
            theme_icon,
            "Theme",
            f"Currently: {current_theme}",
            trailing=ft.Switch(
                value=(page.theme_mode == ft.ThemeMode.DARK),
                on_change=toggle_theme,
                active_color=PRIMARY,
            ),
        ),
        section_header("ABOUT"),
        setting_tile(ft.Icons.INFO_OUTLINE_ROUNDED, "DocLens v0.1.0", "AI Document Scanner"),
        setting_tile(
            ft.Icons.SHIELD_OUTLINED,
            "Data Safety",
            "Images sent to AI gateway. Encrypted in transit. Not shared.",
        ),
        ft.Container(
            content=ad_service.get_banner_ad(),
            padding=SPACE_LG,
        ),
    ]

    appbar = ft.AppBar(
        title=ft.Text("Settings", weight=ft.FontWeight.W_600),
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK_ROUNDED,
            on_click=lambda e: navigate("/scan"),
        ),
        bgcolor=ft.Colors.TRANSPARENT,
    )

    view = ft.View(
        route="/settings",
        controls=[
            appbar,
            ft.ListView(controls=controls, expand=True, padding=ft.Padding.symmetric(horizontal=SPACE_MD)),
        ],
        padding=0,
    )

    return view
