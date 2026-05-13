import flet as ft

PRIMARY = "#2563EB"
ACCENT = "#06B6D4"
TEXT_PRIMARY = "#1E293B"
TEXT_SECONDARY = "#64748B"
SUCCESS = "#10B981"
WARNING = "#F59E0B"
ERROR = "#EF4444"


class AppTheme:
    @staticmethod
    def get_light() -> ft.Theme:
        return ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=PRIMARY,
                on_primary=ft.Colors.WHITE,
                primary_container="#DBEAFE",
                secondary=ACCENT,
                surface="#F8FAFC",
                on_surface=TEXT_PRIMARY,
                on_surface_variant=TEXT_SECONDARY,
                error=ERROR,
                outline="#E2E8F0",
            ),
            visual_density=ft.VisualDensity.COMFORTABLE,
        )

    @staticmethod
    def get_dark() -> ft.Theme:
        return ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=PRIMARY,
                on_primary=ft.Colors.WHITE,
                primary_container="#1E3A5F",
                secondary=ACCENT,
                surface="#0F172A",
                on_surface=ft.Colors.WHITE,
                on_surface_variant="#94A3B8",
                error=ERROR,
                outline="#1E293B",
            ),
            visual_density=ft.VisualDensity.COMFORTABLE,
        )
