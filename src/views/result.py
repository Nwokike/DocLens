import base64
import os

import flet as ft

from core.state import state
from core.theme import ACCENT, PRIMARY, SUCCESS, TEXT_SECONDARY
from core.tokens import RADIUS_LG, RADIUS_MD, SPACE_LG, SPACE_MD, SPACE_SM


def build_result_view(page, navigate):
    if not state.current_image and not state.batch_pages:
        page.route = "/scan"
        page.update()
        return ft.View()

    b64 = base64.b64encode(state.current_image).decode("utf-8") if state.current_image else ""
    all_pages = list(state.batch_pages) + (
        [{"bytes": state.current_image, "mime": state.current_image_mime, "name": state.current_image_name}]
        if state.current_image
        else []
    )
    page_count = len(all_pages)

    pages_column = ft.Column(spacing=SPACE_SM)
    pages_section = ft.Container(content=pages_column, visible=page_count > 1, expand=True)

    def _rebuild_pages():
        pages_column.controls.clear()
        current = list(state.batch_pages)
        if state.current_image:
            current.append(
                {"bytes": state.current_image, "mime": state.current_image_mime, "name": state.current_image_name}
            )
        for idx, p in enumerate(current):
            pb64 = base64.b64encode(p["bytes"]).decode("utf-8")
            pages_column.controls.append(
                ft.Dismissible(
                    content=ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=ft.Image(src=f"data:{p['mime']};base64,{pb64}", fit=ft.BoxFit.COVER),
                                    width=44,
                                    height=44,
                                    border_radius=8,
                                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                                ),
                                ft.Column(
                                    [
                                        ft.Text(f"Page {idx + 1}", size=13, weight=ft.FontWeight.W_500),
                                        ft.Text(f"{len(p['bytes']) // 1024}KB", size=11, color=TEXT_SECONDARY),
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
                        border_radius=RADIUS_MD,
                        border=ft.Border.all(1, ft.Colors.with_opacity(0.06, PRIMARY)),
                    ),
                    dismiss_direction=ft.DismissDirection.END_TO_START,
                    on_dismiss=lambda _, i=idx: _delete_page(i),
                    background=ft.Container(
                        bgcolor=ft.Colors.ERROR,
                        alignment=ft.Alignment.CENTER_RIGHT,
                        padding=ft.Padding(0, 0, 16, 0),
                        content=ft.Icon(ft.Icons.DELETE_ROUNDED, color=ft.Colors.WHITE),
                    ),
                )
            )
        pages_section.visible = len(current) > 1
        page.update()

    def _delete_page(idx):
        if idx < len(state.batch_pages):
            del state.batch_pages[idx]
        elif idx == len(state.batch_pages) and state.current_image:
            state.current_image = None
        _rebuild_pages()

    _rebuild_pages()

    image_display = ft.Container(
        content=ft.Image(
            src=f"data:{state.current_image_mime};base64,{b64}", fit=ft.BoxFit.CONTAIN, border_radius=RADIUS_LG
        )
        if state.current_image
        else ft.Container(),
        border_radius=RADIUS_LG,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.1, PRIMARY)),
        height=260,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    def _add_page(e):
        state.add_page(state.current_image, state.current_image_mime, state.current_image_name)
        state.current_image = None
        page.run_task(navigate, "/scan")

    async def _save_pdf(e):
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
        path = os.path.join(downloads, "DocLens_Scan.pdf")
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
                        title=ft.Text("Scan Review", weight=ft.FontWeight.W_600),
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
                                ft.Container(
                                    content=ft.Row(
                                        [
                                            ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=14, color=SUCCESS),
                                            ft.Text(
                                                f"{page_count} page{'s' if page_count > 1 else ''}",
                                                size=12,
                                                color=SUCCESS,
                                            ),
                                        ],
                                        spacing=4,
                                    ),
                                    padding=ft.Padding(10, 4, 10, 4),
                                    bgcolor=ft.Colors.with_opacity(0.1, SUCCESS),
                                    border_radius=20,
                                ),
                                ft.Container(height=SPACE_MD),
                                pages_section,
                                ft.Container(height=SPACE_SM),
                                ft.OutlinedButton(
                                    "Add Another Page", icon=ft.Icons.ADD_ROUNDED, expand=True, on_click=_add_page
                                ),
                                ft.Container(height=SPACE_LG),
                                ft.Divider(height=1, color=ft.Colors.with_opacity(0.06, PRIMARY)),
                                ft.Container(height=SPACE_MD),
                                ft.Row(
                                    [
                                        ft.Container(
                                            content=ft.Column(
                                                [
                                                    ft.Icon(
                                                        ft.Icons.AUTO_AWESOME_ROUNDED, size=22, color=ft.Colors.WHITE
                                                    ),
                                                    ft.Text(
                                                        "AI Summary",
                                                        size=11,
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
                                                        size=11,
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
                                                        size=11,
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
                                            on_click=lambda e: page.run_task(_save_pdf, e),
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
            )
        ],
        padding=0,
    )
