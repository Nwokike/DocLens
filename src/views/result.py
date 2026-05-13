import base64

import flet as ft

from core.state import state
from core.theme import PRIMARY, ACCENT, SUCCESS, TEXT_SECONDARY
from core.tokens import SPACE_MD, SPACE_LG, SPACE_XL


def build_result_view(page: ft.Page, navigate) -> ft.View:
    if not state.current_image:
        page.route = "/scan"
        page.update()
        return ft.View()

    b64 = base64.b64encode(state.current_image).decode("utf-8")

    image_display = ft.Container(
        content=ft.Image(
            src=f"data:{state.current_image_mime};base64,{b64}",
            fit=ft.BoxFit.CONTAIN,
            border_radius=16,
        ),
        border_radius=16,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.1, PRIMARY)),
        height=350,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    action_btn = ft.Container(
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, size=24, color=ft.Colors.WHITE),
                        ft.Text("AI Summary", size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        padding=ft.Padding(SPACE_XL, SPACE_LG, SPACE_XL, SPACE_LG),
        border_radius=16,
        bgcolor=PRIMARY,
        ink=True,
        on_click=lambda e: navigate("/summary"),
        expand=True,
    )

    translate_btn = ft.Container(
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Icon(ft.Icons.TRANSLATE_ROUNDED, size=24, color=ft.Colors.WHITE),
                        ft.Text("Translate", size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        padding=ft.Padding(SPACE_XL, SPACE_LG, SPACE_XL, SPACE_LG),
        border_radius=16,
        bgcolor=ACCENT,
        ink=True,
        on_click=lambda e: navigate("/translate"),
        expand=True,
    )

    save_btn = ft.Container(
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Icon(ft.Icons.DOWNLOAD_ROUNDED, size=24, color=ft.Colors.WHITE),
                        ft.Text("Save PDF", size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        padding=ft.Padding(SPACE_XL, SPACE_LG, SPACE_XL, SPACE_LG),
        border_radius=16,
        bgcolor=SUCCESS,
        ink=True,
        on_click=lambda e: page.run_task(_save_pdf, page),
        expand=True,
    )

    content = ft.Column(
        [
            ft.AppBar(
                title=ft.Text("Document Scan", weight=ft.FontWeight.W_600),
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK_ROUNDED,
                    on_click=lambda e: navigate("/scan"),
                ),
                bgcolor=ft.Colors.TRANSPARENT,
            ),
            ft.Container(
                content=ft.Column(
                    [
                        image_display,
                        ft.Container(height=SPACE_LG),
                        ft.Row(
                            [action_btn, translate_btn, save_btn],
                            spacing=SPACE_MD,
                        ),
                    ],
                    spacing=0,
                    expand=True,
                ),
                padding=ft.Padding(SPACE_LG, 0, SPACE_LG, SPACE_LG),
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )

    return ft.View(route="/result", controls=[content], padding=0)


async def _save_pdf(page: ft.Page):
    from services.share import ShareService

    share = ShareService(page)
    await share.save_as_pdf(state.current_image, "DocLens_Scan")
