import flet as ft

from core.state import state
from core.theme import PRIMARY, TEXT_SECONDARY
from core.tokens import SPACE_LG, SPACE_MD
from services import ai_service

LANGUAGES = [
    ("en", "English"),
    ("es", "Spanish"),
    ("fr", "French"),
    ("de", "German"),
    ("zh", "Chinese"),
    ("ja", "Japanese"),
    ("ar", "Arabic"),
    ("pt", "Portuguese"),
    ("it", "Italian"),
    ("ru", "Russian"),
    ("ko", "Korean"),
    ("nl", "Dutch"),
]


def build_translate_view(page: ft.Page, navigate) -> ft.View:

    selected_lang = "Spanish"

    dropdown = ft.Dropdown(
        label="Translate to",
        value=selected_lang,
        options=[ft.dropdown.Option(label) for _, label in LANGUAGES],
        width=300,
    )

    status_text = ft.Text(
        "",
        size=14,
        color=TEXT_SECONDARY,
        text_align=ft.TextAlign.CENTER,
    )

    progress = ft.ProgressRing(
        width=32,
        height=32,
        stroke_width=3,
        color=PRIMARY,
        visible=False,
    )

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

    translate_btn = ft.ElevatedButton(
        "Translate",
        icon=ft.Icons.TRANSLATE_ROUNDED,
        on_click=lambda e: page.run_task(
            _do_translate,
            page,
            dropdown,
            status_text,
            progress,
            translate_btn,
            original_section,
            translated_section,
            original_text,
            translated_text,
        ),
    )

    content = ft.Column(
        [
            ft.AppBar(
                title=ft.Text("Translate", weight=ft.FontWeight.W_600),
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK_ROUNDED,
                    on_click=lambda e: page.run_task(navigate, "/result"),
                ),
                bgcolor=ft.Colors.TRANSPARENT,
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Column(
                                [dropdown, ft.Container(height=SPACE_LG), translate_btn],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=0,
                            ),
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Container(height=SPACE_LG),
                        ft.Row(
                            [progress, status_text],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=SPACE_MD,
                        ),
                        ft.Container(height=SPACE_LG),
                        original_section,
                        ft.Container(height=SPACE_MD),
                        translated_section,
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

    return ft.View(route="/translate", controls=[content], padding=0)


async def _do_translate(
    page,
    dropdown,
    status_text,
    progress,
    translate_btn,
    original_section,
    translated_section,
    original_text,
    translated_text,
):
    target = dropdown.value or "Spanish"
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
    status_text.value = ""
    page.update()
