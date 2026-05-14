import base64
import os

import flet as ft

from core.state import state
from core.theme import ACCENT, PRIMARY, SUCCESS, TEXT_SECONDARY
from core.tokens import RADIUS_LG, SPACE_LG, SPACE_MD, SPACE_SM


def build_result_view(page, navigate):
    if not state.current_image and not state.batch_pages:
        page.route = "/scan"
        page.update()
        return ft.View()

    b64 = base64.b64encode(state.current_image).decode("utf-8") if state.current_image else ""
    page_count = len(state.batch_pages) + (1 if state.current_image else 0)

    pages_list = ft.Column(spacing=SPACE_SM)
    pages_container = ft.Container(content=pages_list, visible=False, expand=True)

    def _refresh_pages():
        pages_list.controls.clear()
        all_pages = list(state.batch_pages)
        if state.current_image:
            all_pages.append(
                {"bytes": state.current_image, "mime": state.current_image_mime, "name": state.current_image_name}
            )
        for i, p in enumerate(all_pages):
            pb64 = base64.b64encode(p["bytes"]).decode("utf-8")
            pages_list.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                content=ft.Image(src=f"data:{p['mime']};base64,{pb64}", fit=ft.BoxFit.COVER),
                                width=48,
                                height=48,
                                border_radius=8,
                                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                            ),
                            ft.Column(
                                [
                                    ft.Text(f"Page {i + 1}", size=13, weight=ft.FontWeight.W_500),
                                    ft.Text(f"{len(p['bytes'])} bytes", size=11, color=TEXT_SECONDARY),
                                ],
                                spacing=1,
                                expand=True,
                            ),
                        ],
                        spacing=SPACE_MD,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=SPACE_MD,
                    bgcolor=ft.Colors.SURFACE,
                    border_radius=RADIUS_LG,
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.06, PRIMARY)),
                )
            )
        pages_container.visible = len(all_pages) > 1
        page.update()

    _refresh_pages()

    image_display = ft.Container(
        content=ft.Image(
            src=f"data:{state.current_image_mime};base64,{b64}", fit=ft.BoxFit.CONTAIN, border_radius=RADIUS_LG
        ),
        border_radius=RADIUS_LG,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.1, PRIMARY)),
        height=280,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    status_badge = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=14, color=SUCCESS),
                ft.Text(
                    f"{page_count} page{'s' if page_count > 1 else ''} captured",
                    size=12,
                    color=SUCCESS,
                    weight=ft.FontWeight.W_500,
                ),
            ],
            spacing=4,
        ),
        padding=ft.Padding(10, 4, 10, 4),
        bgcolor=ft.Colors.with_opacity(0.1, SUCCESS),
        border_radius=20,
    )

    def _add_page(e):
        state.add_page(state.current_image, state.current_image_mime, state.current_image_name)
        state.current_image = None
        page.run_task(navigate, "/scan")

    async def _combine_pdf(e):
        pages = list(state.batch_pages)
        if state.current_image:
            pages.append(
                {"bytes": state.current_image, "mime": state.current_image_mime, "name": state.current_image_name}
            )
        from fpdf import FPDF

        pdf = FPDF()
        for p in pages:
            pdf.add_page()
            pdf.image(p["bytes"], x=10, y=10, w=190)
        downloads = os.path.expanduser("~/Downloads")
        os.makedirs(downloads, exist_ok=True)
        path = os.path.join(downloads, "DocLens_Combined.pdf")
        try:
            pdf.output(path)
            page.show_dialog(ft.SnackBar(content=ft.Text(f"Saved {len(pages)} pages to Downloads"), duration=3000))
        except Exception as e:
            page.show_dialog(ft.SnackBar(content=ft.Text(f"Save failed: {e}"), bgcolor=ft.Colors.ERROR))

    return ft.View(
        route="/result",
        controls=[
            ft.Column(
                [
                    ft.AppBar(
                        title=ft.Text("Document Scan", weight=ft.FontWeight.W_600),
                        leading=ft.IconButton(
                            icon=ft.Icons.ARROW_BACK_ROUNDED, on_click=lambda e: page.run_task(navigate, "/scan")
                        ),
                        bgcolor=ft.Colors.TRANSPARENT,
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                image_display,
                                ft.Container(height=SPACE_SM),
                                status_badge,
                                ft.Container(height=SPACE_MD),
                                pages_container,
                                ft.Container(height=SPACE_MD),
                                ft.Row(
                                    [
                                        ft.OutlinedButton(
                                            "Add Page", icon=ft.Icons.ADD_ROUNDED, expand=True, on_click=_add_page
                                        ),
                                        ft.FilledButton(
                                            "Combine PDF",
                                            icon=ft.Icons.PICTURE_AS_PDF_ROUNDED,
                                            expand=True,
                                            on_click=lambda e: page.run_task(_combine_pdf, e),
                                        ),
                                    ],
                                    spacing=SPACE_MD,
                                ),
                                ft.Container(height=SPACE_LG),
                                ft.Divider(height=1, color=ft.Colors.with_opacity(0.06, PRIMARY)),
                                ft.Container(height=SPACE_MD),
                                ft.Text("AI TOOLS", size=12, weight=ft.FontWeight.BOLD, color=TEXT_SECONDARY),
                                ft.Container(height=SPACE_SM),
                                ft.Row(
                                    [
                                        ft.Container(
                                            content=ft.Column(
                                                [
                                                    ft.Icon(
                                                        ft.Icons.AUTO_AWESOME_ROUNDED, size=22, color=ft.Colors.WHITE
                                                    ),
                                                    ft.Text(
                                                        "Summary",
                                                        size=12,
                                                        color=ft.Colors.WHITE,
                                                        weight=ft.FontWeight.W_600,
                                                    ),
                                                ],
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                spacing=2,
                                            ),
                                            padding=ft.Padding(SPACE_MD, 12, SPACE_MD, 12),
                                            border_radius=RADIUS_LG,
                                            bgcolor=PRIMARY,
                                            expand=True,
                                            ink=True,
                                            on_click=lambda e: page.run_task(navigate, "/summary"),
                                        ),
                                        ft.Container(
                                            content=ft.Column(
                                                [
                                                    ft.Icon(ft.Icons.TRANSLATE_ROUNDED, size=22, color=ft.Colors.WHITE),
                                                    ft.Text(
                                                        "Translate",
                                                        size=12,
                                                        color=ft.Colors.WHITE,
                                                        weight=ft.FontWeight.W_600,
                                                    ),
                                                ],
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                spacing=2,
                                            ),
                                            padding=ft.Padding(SPACE_MD, 12, SPACE_MD, 12),
                                            border_radius=RADIUS_LG,
                                            bgcolor=ACCENT,
                                            expand=True,
                                            ink=True,
                                            on_click=lambda e: page.run_task(navigate, "/translate"),
                                        ),
                                        ft.Container(
                                            content=ft.Column(
                                                [
                                                    ft.Icon(ft.Icons.DOWNLOAD_ROUNDED, size=22, color=ft.Colors.WHITE),
                                                    ft.Text(
                                                        "Save PDF",
                                                        size=12,
                                                        color=ft.Colors.WHITE,
                                                        weight=ft.FontWeight.W_600,
                                                    ),
                                                ],
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                spacing=2,
                                            ),
                                            padding=ft.Padding(SPACE_MD, 12, SPACE_MD, 12),
                                            border_radius=RADIUS_LG,
                                            bgcolor=SUCCESS,
                                            expand=True,
                                            ink=True,
                                            on_click=lambda e: page.run_task(_combine_pdf, e),
                                        ),
                                    ],
                                    spacing=SPACE_MD,
                                ),
                            ],
                            spacing=0,
                            expand=True,
                        ),
                        padding=SPACE_LG,
                        expand=True,
                    ),
                ],
                spacing=0,
                expand=True,
            ),
        ],
        padding=0,
    )
