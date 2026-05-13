import logging

import flet as ft

logger = logging.getLogger(__name__)

_HAS_ADS = False
try:
    from flet_ads import BannerAd

    _HAS_ADS = True
except ImportError:
    pass


def AdBanner(unit_id: str) -> ft.Control:
    if not _HAS_ADS:
        return ft.Container(width=0, height=0)
    try:
        ad = BannerAd(unit_id=unit_id, on_error=lambda e: None)
        return ft.Container(
            content=ad, width=320, height=50, alignment=ft.Alignment.CENTER, padding=ft.Padding(0, 10, 0, 10)
        )
    except Exception:
        return ft.Container(width=0, height=0)
