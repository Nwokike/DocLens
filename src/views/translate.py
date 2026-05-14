import flet as ft

from core.state import state
from core.theme import PRIMARY, TEXT_SECONDARY
from core.tokens import RADIUS_LG, SPACE_LG, SPACE_MD
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


def build_translate_view(page, navigate):
    dropdown = ft.Dropdown(
        label="Translate to", value="Spanish", options=[ft.dropdown.Option(lang) for lang in LANGUAGES], width=280
    )
    custom = ft.TextField(hint_text="Or type any language...", dense=True, width=280)

    status_text = ft.Text("", size=14, color=TEXT_SECONDARY, text_align=ft.TextAlign.CENTER)
    progress = ft.ProgressRing(width=24, height=24, stroke_width=2, color=PRIMARY, visible=False)

    original_md = ft.Markdown(
        "", selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB, fit_content=True, visible=False
    )
    translated_md = ft.Markdown(
        "", selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB, fit_content=True, visible=False
    )

    original_section = ft.Container(
        content=ft.Column(
            [
                ft.Text("Original", size=11, weight=ft.FontWeight.BOLD, color=TEXT_SECONDARY),
                ft.Container(height=SPACE_MD),
                original_md,
            ],
            spacing=0,
        ),
        padding=SPACE_MD,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.08, PRIMARY)),
        border_radius=RADIUS_LG,
        visible=False,
    )
    translated_section = ft.Container(
        content=ft.Column(
            [
                ft.Text("Translation", size=11, weight=ft.FontWeight.BOLD, color=PRIMARY),
                ft.Container(height=SPACE_MD),
                translated_md,
            ],
            spacing=0,
        ),
        padding=SPACE_MD,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.15, PRIMARY)),
        border_radius=RADIUS_LG,
        visible=False,
        bgcolor=ft.Colors.with_opacity(0.03, PRIMARY),
    )

    copy_btn = ft.IconButton(
        icon=ft.Icons.COPY_ROUNDED,
        tooltip="Copy",
        visible=False,
        on_click=lambda e: page.run_task(_cp, page, state.current_translation),
    )
    save_btn = ft.IconButton(
        icon=ft.Icons.DESCRIPTION_ROUNDED,
        tooltip="Save",
        visible=False,
        on_click=lambda e: page.run_task(_sv, page, state.current_translation),
    )

    btn = ft.FilledButton("Translate", icon=ft.Icons.TRANSLATE_ROUNDED, expand=True)

    async def _do(e):
        target = custom.value.strip() if custom.value and custom.value.strip() else (dropdown.value or "Spanish")
        progress.visible = True
        btn.disabled = True
        status_text.value = f"Translating to {target}..."
        page.update()

        def on_stage(msg):
            status_text.value = msg
            page.update()

        def on_stream(c):
            translated_md.value = c
            translated_md.visible = True
            page.update()

        if not state.extracted_text:
            state.extracted_text = await ai_service.analyze_document(
                state.current_image, state.current_image_mime, on_stage=on_stage
            )

        if state.extracted_text:
            original_md.value = state.extracted_text
            original_md.visible = True
            original_section.visible = True
            page.update()

        state.current_translation = await ai_service.translate(
            state.extracted_text, target, stream_callback=on_stream, on_stage=on_stage
        )

        progress.visible = False
        btn.disabled = False
        copy_btn.visible = True
        save_btn.visible = True
        translated_section.visible = True
        status_text.value = ""
        page.update()

    btn.on_click = lambda e: page.run_task(_do, e)

    return ft.View(
        route="/translate",
        controls=[
            ft.Column(
                [
                    ft.AppBar(
                        title=ft.Text("Translate", weight=ft.FontWeight.W_600),
                        leading=ft.IconButton(
                            icon=ft.Icons.ARROW_BACK_ROUNDED, on_click=lambda e: page.run_task(navigate, "/result")
                        ),
                        actions=[copy_btn, save_btn],
                        bgcolor=ft.Colors.TRANSPARENT,
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Container(
                                    content=ft.Column(
                                        [dropdown, custom, ft.Container(height=SPACE_MD), btn],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=0,
                                    ),
                                    alignment=ft.Alignment.CENTER,
                                ),
                                ft.Container(height=SPACE_LG),
                                ft.Row(
                                    [progress, status_text], alignment=ft.MainAxisAlignment.CENTER, spacing=SPACE_MD
                                ),
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
        ],
        padding=0,
    )


async def _cp(page, text):
    s = ShareService(page)
    await s.copy_text(text)


async def _sv(page, text):
    s = ShareService(page)
    await s.save_as_document(text, "DocLens_Translation")
