import flet as ft

from core.state import state
from core.theme import PRIMARY, TEXT_SECONDARY
from core.tokens import SPACE_LG, SPACE_MD
from services import ai_service
from services.share import ShareService


def build_summary_view(page, navigate):
    status_text = ft.Text("Analyzing document...", size=14, color=TEXT_SECONDARY, text_align=ft.TextAlign.CENTER)
    progress = ft.ProgressRing(width=28, height=28, stroke_width=3, color=PRIMARY)
    stage_container = ft.Container(
        content=ft.Column(
            [progress, ft.Container(height=SPACE_MD), status_text],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        alignment=ft.Alignment.CENTER,
        expand=True,
    )

    md = ft.Markdown("", selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB, fit_content=True)
    result_container = ft.Container(content=md, visible=False, padding=SPACE_LG, expand=True)

    def _save(_, text):
        page.run_task(_save_fn, page, text)

    save_btn = ft.IconButton(
        icon=ft.Icons.DESCRIPTION_ROUNDED,
        tooltip="Save as Document",
        visible=False,
        on_click=lambda e: _save(e, state.current_summary),
    )
    copy_btn = ft.IconButton(
        icon=ft.Icons.COPY_ROUNDED,
        tooltip="Copy",
        visible=False,
        on_click=lambda e: page.run_task(_copy_fn, page, state.current_summary),
    )

    content = ft.Column(
        [
            ft.AppBar(
                title=ft.Text("AI Summary", weight=ft.FontWeight.W_600),
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK_ROUNDED, on_click=lambda e: page.run_task(navigate, "/result")
                ),
                actions=[copy_btn, save_btn],
                bgcolor=ft.Colors.TRANSPARENT,
            ),
            stage_container,
            result_container,
        ],
        spacing=0,
        expand=True,
    )

    view = ft.View(route="/summary", controls=[content], padding=0)

    async def run():
        def on_stage(msg):
            status_text.value = msg
            page.update()

        def on_stream(c):
            md.value = c
            result_container.visible = True
            page.update()

        if not state.extracted_text:
            state.extracted_text = await ai_service.analyze_document(
                state.current_image, state.current_image_mime, on_stage=on_stage
            )
        state.current_summary = await ai_service.summarize(
            state.extracted_text, stream_callback=on_stream, on_stage=on_stage
        )

        stage_container.visible = False
        save_btn.visible = True
        copy_btn.visible = True
        page.update()

    page.run_task(run)
    return view


async def _copy_fn(page, text):
    s = ShareService(page)
    await s.copy_text(text)


async def _save_fn(page, text):
    s = ShareService(page)
    await s.save_as_document(text, "DocLens_Summary")
