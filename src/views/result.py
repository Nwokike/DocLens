import base64

import flet as ft

from core.state import state
from core.theme import ACCENT, PRIMARY, SUCCESS, TEXT_SECONDARY
from core.tokens import SPACE_LG, SPACE_MD, SPACE_SM, SPACE_XL


def build_result_view(page: ft.Page, navigate) -> ft.View:
    if not state.current_image and not state.batch_pages:
        page.route = "/scan"
        page.update()
        return ft.View()

    b64 = base64.b64encode(state.current_image).decode("utf-8") if state.current_image else ""

    page_count = len(state.batch_pages) + (1 if state.current_image else 0)

    image_display = ft.Container(
        content=ft.Image(src=f"data:{state.current_image_mime};base64,{b64}", fit=ft.BoxFit.CONTAIN, border_radius=16),
        border_radius=16,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.1, PRIMARY)),
        height=300,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    page_counter = ft.Container(
        content=ft.Text(f"Page {page_count}", size=12, color=TEXT_SECONDARY, weight=ft.FontWeight.W_500),
        alignment=ft.Alignment.CENTER,
        padding=ft.Padding(0, SPACE_SM, 0, 0),
    )

    def _add_page(e):
        state.add_page(state.current_image, state.current_image_mime, state.current_image_name)
        state.current_image = None
        page.run_task(navigate, "/scan")

    add_page_btn = ft.OutlinedButton("Add Another Page", icon=ft.Icons.ADD_ROUNDED, on_click=_add_page, expand=True)

    async def _combine_pdf(e):
        from services.share import ShareService

        share = ShareService(page)
        pages = list(state.batch_pages)
        if state.current_image:
            pages.append(
                {"bytes": state.current_image, "mime": state.current_image_mime, "name": state.current_image_name}
            )
        if len(pages) == 1:
            await share.save_as_pdf(pages[0]["bytes"], "DocLens_Scan")
        else:
            from fpdf import FPDF

            pdf = FPDF()
            for p in pages:
                pdf.add_page()
                pdf.image(p["bytes"], x=10, y=10, w=190)
            path = "/storage/emulated/0/Download/DocLens_Combined.pdf"
            try:
                pdf.output(path)
                page.show_dialog(ft.SnackBar(content=ft.Text(f"Saved {len(pages)} pages to Downloads"), duration=3000))
            except Exception as e:
                page.show_dialog(ft.SnackBar(content=ft.Text(f"Save failed: {e}"), bgcolor=ft.Colors.ERROR))

    action_btn = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, size=24, color=ft.Colors.WHITE),
                ft.Text("AI Summary", size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        ),
        padding=ft.Padding(SPACE_XL, SPACE_LG, SPACE_XL, SPACE_LG),
        border_radius=16,
        bgcolor=PRIMARY,
        ink=True,
        on_click=lambda e: page.run_task(navigate, "/summary"),
        expand=True,
    )

    translate_btn = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.TRANSLATE_ROUNDED, size=24, color=ft.Colors.WHITE),
                ft.Text("Translate", size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        ),
        padding=ft.Padding(SPACE_XL, SPACE_LG, SPACE_XL, SPACE_LG),
        border_radius=16,
        bgcolor=ACCENT,
        ink=True,
        on_click=lambda e: page.run_task(navigate, "/translate"),
        expand=True,
    )

    save_btn = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.DOWNLOAD_ROUNDED, size=24, color=ft.Colors.WHITE),
                ft.Text("Save PDF", size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        ),
        padding=ft.Padding(SPACE_XL, SPACE_LG, SPACE_XL, SPACE_LG),
        border_radius=16,
        bgcolor=SUCCESS,
        ink=True,
        on_click=lambda e: page.run_task(_combine_pdf, e),
        expand=True,
    )

    content = ft.Column(
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
                        page_counter,
                        ft.Container(height=SPACE_MD),
                        add_page_btn,
                        ft.Container(height=SPACE_LG),
                        ft.Row([action_btn, translate_btn, save_btn], spacing=SPACE_MD),
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
