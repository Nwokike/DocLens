import flet as ft

from core.state import state
from core.theme import PRIMARY, TEXT_SECONDARY
from core.tokens import SPACE_LG, SPACE_MD
from services import ai_service
from services.share import ShareService


def build_summary_view(page: ft.Page, navigate) -> ft.View:

    status_text = ft.Text(
        "Preparing...",
        size=14,
        color=TEXT_SECONDARY,
        text_align=ft.TextAlign.CENTER,
    )

    progress = ft.ProgressRing(
        width=32,
        height=32,
        stroke_width=3,
        color=PRIMARY,
    )

    status_area = ft.Container(
        content=ft.Column(
            [progress, ft.Container(height=SPACE_MD), status_text],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        alignment=ft.Alignment.CENTER,
        expand=True,
    )

    markdown_content = ft.Markdown(
        "",
        selectable=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
        fit_content=True,
    )

    result_area = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=markdown_content,
                    padding=SPACE_LG,
                    expand=True,
                ),
            ],
            spacing=0,
            expand=True,
        ),
        visible=False,
        expand=True,
    )

    share_btn = ft.IconButton(
        icon=ft.Icons.SHARE_ROUNDED,
        tooltip="Share",
        on_click=lambda e: page.run_task(_share_summary, page, state.current_summary),
        visible=False,
    )

    copy_btn = ft.IconButton(
        icon=ft.Icons.COPY_ROUNDED,
        tooltip="Copy",
        on_click=lambda e: page.run_task(_copy_summary, page, state.current_summary),
        visible=False,
    )

    save_doc_btn = ft.IconButton(
        icon=ft.Icons.DESCRIPTION_ROUNDED,
        tooltip="Save as Document",
        on_click=lambda e: page.run_task(_save_doc, page, state.current_summary),
        visible=False,
    )

    save_pdf_btn = ft.IconButton(
        icon=ft.Icons.PICTURE_AS_PDF_ROUNDED,
        tooltip="Save as PDF",
        on_click=lambda e: page.run_task(_save_summary_pdf, page, state.current_summary),
        visible=False,
    )

    content = ft.Column(
        [
            ft.AppBar(
                title=ft.Text("AI Summary", weight=ft.FontWeight.W_600),
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK_ROUNDED,
                    on_click=lambda e: page.run_task(navigate, "/result"),
                ),
                actions=[copy_btn, save_doc_btn, save_pdf_btn, share_btn],
                bgcolor=ft.Colors.TRANSPARENT,
            ),
            status_area,
            result_area,
        ],
        spacing=0,
        expand=True,
    )

    view = ft.View(route="/summary", controls=[content], padding=0)

    page.run_task(
        _generate_summary,
        page,
        status_text,
        progress,
        status_area,
        result_area,
        markdown_content,
        share_btn,
        copy_btn,
        save_doc_btn,
        save_pdf_btn,
    )

    return view


async def _generate_summary(
    page,
    status_text,
    progress,
    status_area,
    result_area,
    markdown_content,
    share_btn,
    copy_btn,
    save_doc_btn,
    save_pdf_btn,
):
    def on_stage(msg):
        status_text.value = msg
        page.update()

    def on_stream(content):
        markdown_content.value = content
        page.update()

    if not state.extracted_text:
        state.extracted_text = await ai_service.analyze_document(
            state.current_image,
            state.current_image_mime,
            on_stage=on_stage,
        )

    state.current_summary = await ai_service.summarize(
        state.extracted_text,
        stream_callback=on_stream,
        on_stage=on_stage,
    )

    status_area.visible = False
    result_area.visible = True
    share_btn.visible = True
    copy_btn.visible = True
    save_doc_btn.visible = True
    save_pdf_btn.visible = True
    page.update()


async def _copy_summary(page, text):
    share = ShareService(page)
    await share.copy_text(text)


async def _share_summary(page, text):
    share = ShareService(page)
    await share.share_text(text)


async def _save_doc(page, text):
    share = ShareService(page)
    await share.save_as_document(text, "DocLens_Summary")


async def _save_summary_pdf(page, text):
    share = ShareService(page)
    await share.save_text_as_pdf(text, "DocLens_Summary")
