import flet as ft

from core.state import state
from core.theme import PRIMARY, TEXT_SECONDARY
from core.tokens import SPACE_LG, SPACE_MD
from services import ai_service
from services.share import ShareService

LANGUAGES = [
    "Spanish",
    "French",
    "German",
    "Chinese",
    "Japanese",
    "Arabic",
    "Portuguese",
    "Italian",
    "Russian",
    "Korean",
    "Dutch",
]


def build_translate_view(page: ft.Page, navigate) -> ft.View:

    dropdown = ft.Dropdown(
        label="Select language",
        value="Spanish",
        options=[ft.dropdown.Option(lang) for lang in LANGUAGES],
        width=300,
    )

    custom_field = ft.TextField(
        hint_text="Or type a custom language...",
        width=300,
        dense=True,
    )

    status_text = ft.Text("", size=14, color=TEXT_SECONDARY, text_align=ft.TextAlign.CENTER)

    progress = ft.ProgressRing(width=32, height=32, stroke_width=3, color=PRIMARY, visible=False)

    original_text = ft.Markdown(
        "",
        selectable=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
        fit_content=True,
        visible=False,
    )

    translated_text = ft.Markdown(
        "",
        selectable=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
        fit_content=True,
        visible=False,
    )

    original_section = ft.Container(
        content=ft.Column(
            [
                ft.Text("Original", size=12, weight=ft.FontWeight.BOLD, color=TEXT_SECONDARY),
                ft.Container(height=SPACE_MD),
                original_text,
            ],
            spacing=0,
        ),
        padding=ft.Padding(SPACE_LG, SPACE_MD, SPACE_LG, SPACE_MD),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.1, PRIMARY)),
        border_radius=12,
        visible=False,
    )

    translated_section = ft.Container(
        content=ft.Column(
            [
                ft.Text("Translation", size=12, weight=ft.FontWeight.BOLD, color=PRIMARY),
                ft.Container(height=SPACE_MD),
                translated_text,
            ],
            spacing=0,
        ),
        padding=ft.Padding(SPACE_LG, SPACE_MD, SPACE_LG, SPACE_MD),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.2, PRIMARY)),
        border_radius=12,
        bgcolor=ft.Colors.with_opacity(0.05, PRIMARY),
        visible=False,
    )

    translate_btn = ft.FilledButton(
        "Translate",
        icon=ft.Icons.TRANSLATE_ROUNDED,
        on_click=lambda e: page.run_task(
            _do_translate,
            page,
            dropdown,
            custom_field,
            status_text,
            progress,
            translate_btn,
            original_section,
            translated_section,
            original_text,
            translated_text,
            copy_btn,
            save_doc_btn,
        ),
    )

    copy_btn = ft.IconButton(
        icon=ft.Icons.COPY_ROUNDED,
        tooltip="Copy",
        visible=False,
        on_click=lambda e: page.run_task(_copy_translation, page, state.current_translation),
    )

    save_doc_btn = ft.IconButton(
        icon=ft.Icons.DESCRIPTION_ROUNDED,
        tooltip="Save as Document",
        visible=False,
        on_click=lambda e: page.run_task(_save_translation, page, state.current_translation),
    )

    content = ft.Column(
        [
            ft.AppBar(
                title=ft.Text("Translate", weight=ft.FontWeight.W_600),
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK_ROUNDED,
                    on_click=lambda e: page.run_task(navigate, "/result"),
                ),
                actions=[copy_btn, save_doc_btn],
                bgcolor=ft.Colors.TRANSPARENT,
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Column(
                                [dropdown, custom_field, ft.Container(height=SPACE_LG), translate_btn],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=0,
                            ),
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Container(height=SPACE_LG),
                        ft.Row([progress, status_text], alignment=ft.MainAxisAlignment.CENTER, spacing=SPACE_MD),
                        ft.Container(height=SPACE_LG),
                        original_section,
                        ft.Container(height=SPACE_MD),
                        translated_section,
                    ],
                    spacing=0,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=SPACE_LG,
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )

    return ft.View(route="/translate", controls=[content], padding=0)


async def _do_translate(
    page,
    dropdown,
    custom_field,
    status_text,
    progress,
    translate_btn,
    original_section,
    translated_section,
    original_text,
    translated_text,
    copy_btn,
    save_doc_btn,
):
    target = (
        custom_field.value.strip()
        if custom_field.value and custom_field.value.strip()
        else (dropdown.value or "Spanish")
    )
    progress.visible = True
    translate_btn.disabled = True
    page.update()

    def on_stage(msg):
        status_text.value = msg
        page.update()

    def on_stream(content):
        translated_text.value = content
        translated_text.visible = True
        page.update()

    if not state.extracted_text:
        state.extracted_text = await ai_service.analyze_document(
            state.current_image,
            state.current_image_mime,
            on_stage=on_stage,
        )

    if state.extracted_text:
        original_text.value = state.extracted_text
        original_text.visible = True
        original_section.visible = True
        page.update()

    state.current_translation = await ai_service.translate(
        state.extracted_text,
        target,
        stream_callback=on_stream,
        on_stage=on_stage,
    )

    progress.visible = False
    translate_btn.disabled = False
    translated_section.visible = True
    copy_btn.visible = True
    save_doc_btn.visible = True
    status_text.value = ""
    page.update()


async def _copy_translation(page, text):
    share = ShareService(page)
    await share.copy_text(text)


async def _save_translation(page, text):
    share = ShareService(page)
    await share.save_as_document(text, "DocLens_Translation")
