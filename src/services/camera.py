import logging

import flet as ft

logger = logging.getLogger(__name__)

_HAS_CAMERA = False
try:
    from flet_camera import Camera
    from flet_camera.types import ResolutionPreset

    _HAS_CAMERA = True
except ImportError:
    pass


class CameraService:
    def __init__(self, page: ft.Page):
        self._page = page

    @property
    def available(self) -> bool:
        return _HAS_CAMERA

    async def capture_photo(self) -> tuple[bytes, str] | None:
        if not _HAS_CAMERA:
            logger.info("Camera not available")
            self._page.show_dialog(ft.SnackBar(content=ft.Text("Camera is not available on this platform")))
            return None

        camera = None
        try:
            camera = Camera()
            self._page.overlay.append(camera)
            self._page.update()

            cameras = await camera.get_available_cameras()
            if not cameras:
                return None

            await camera.initialize(
                description=cameras[0],
                resolution_preset=ResolutionPreset.MEDIUM,
                enable_audio=False,
            )

            image_bytes = await camera.take_picture()

            if image_bytes:
                logger.info("Camera captured %d bytes", len(image_bytes))
                return (image_bytes, "image/jpeg")

        except Exception as e:
            logger.error("Camera capture failed: %s", e)
        finally:
            if camera:
                try:
                    if camera in self._page.overlay:
                        self._page.overlay.remove(camera)
                    self._page.update()
                except Exception:
                    pass

        return None
