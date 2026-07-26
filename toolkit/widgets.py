"""
widgets.py

Reusable Qt display widgets.

Provides:

- ImageLabel
- ImagePanel

Features:
- Responsive image scaling
- Medical dark-theme styling
- Crop support
- Automatic resize updates
"""

import cv2

from PyQt6.QtWidgets import (
    QLabel,
    QWidget,
    QAbstractButton,
    QVBoxLayout,
    QRubberBand,
    QSizePolicy,
)

from PyQt6.QtGui import (
    QPixmap,
    QImage,
    QMouseEvent,
    QPainter,
    QColor,
    QPen,
)

from PyQt6.QtCore import (
    Qt,
    QRect,
    QPoint,
    QSize,
)

DISPLAY_SIZE = 450


class ImageLabel(QLabel):
    """
    QLabel displaying OpenCV images with
    image-to-widget coordinate mapping.
    """

    def __init__(
        self,
        on_crop_selected=None,
    ):
        super().__init__("No image loaded")

        self.setMinimumSize(350, 350)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.setStyleSheet(
            """
            QLabel {
                background-color: #181818;
                color: #888888;
                border: 1px solid #444444;
                border-radius: 8px;
            }
            """
        )

        self.cv_img = None

        self.img_w = 0
        self.img_h = 0

        self.offset_x = 0
        self.offset_y = 0

        self.scale = 1.0

        self.crop_active = False

        self.on_crop_selected = (
            on_crop_selected
        )

        self._rubber_band = QRubberBand(
            QRubberBand.Shape.Rectangle,
            self,
        )

        self._origin = QPoint()

    # ----------------------------------
    # Image display
    # ----------------------------------

    def set_cv_image(self, cv_img):

        self.cv_img = cv_img

        if cv_img is None:

            self.setText(
                "No image loaded"
            )

            self.setPixmap(QPixmap())

            self.img_w = 0
            self.img_h = 0

            return

        self._update_pixmap()

    def _update_pixmap(self):

        if self.cv_img is None:
            return

        cv_img = self.cv_img

        if cv_img.ndim == 2:

            h, w = cv_img.shape

            qimg = QImage(
                cv_img.data,
                w,
                h,
                w,
                QImage.Format.Format_Grayscale8,
            )

        else:

            channels = cv_img.shape[2]

            rgb = cv2.cvtColor(
                cv_img,
                cv2.COLOR_BGRA2RGB
                if channels == 4
                else cv2.COLOR_BGR2RGB,
            )

            h, w, ch = rgb.shape

            qimg = QImage(
                rgb.data,
                w,
                h,
                ch * w,
                QImage.Format.Format_RGB888,
            )

        pixmap = QPixmap.fromImage(qimg)

        scaled = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.setPixmap(scaled)

        self.img_w = w
        self.img_h = h

        self.scale = (
            scaled.width() / w
            if w
            else 1.0
        )

        self.offset_x = (
            self.width()
            - scaled.width()
        ) // 2

        self.offset_y = (
            self.height()
            - scaled.height()
        ) // 2

    def resizeEvent(self, event):

        self._update_pixmap()

        super().resizeEvent(event)

    # ----------------------------------
    # Coordinate conversion
    # ----------------------------------

    def _label_to_image_point(
        self,
        pos: QPoint,
    ) -> QPoint:

        x = (
            (pos.x() - self.offset_x)
            / self.scale
        )

        y = (
            (pos.y() - self.offset_y)
            / self.scale
        )

        x = max(
            0,
            min(self.img_w, x),
        )

        y = max(
            0,
            min(self.img_h, y),
        )

        return QPoint(
            int(x),
            int(y),
        )

    # ----------------------------------
    # Crop support
    # ----------------------------------

    def mousePressEvent(
        self,
        event: QMouseEvent,
    ):

        if (
            self.crop_active
            and self.img_w
        ):

            self._origin = event.pos()

            self._rubber_band.setGeometry(
                QRect(
                    self._origin,
                    QSize(),
                )
            )

            self._rubber_band.show()

        super().mousePressEvent(event)

    def mouseMoveEvent(
        self,
        event: QMouseEvent,
    ):

        if (
            self.crop_active
            and self._rubber_band.isVisible()
        ):

            rect = QRect(
                self._origin,
                event.pos(),
            ).normalized()

            self._rubber_band.setGeometry(
                rect
            )

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(
        self,
        event: QMouseEvent,
    ):

        if (
            self.crop_active
            and self._rubber_band.isVisible()
        ):

            self._rubber_band.hide()

            rect = QRect(
                self._origin,
                event.pos(),
            ).normalized()

            p1 = self._label_to_image_point(
                rect.topLeft()
            )

            p2 = self._label_to_image_point(
                rect.bottomRight()
            )

            image_rect = QRect(
                p1,
                p2,
            ).normalized()

            if (
                image_rect.width() > 2
                and
                image_rect.height() > 2
                and
                self.on_crop_selected
            ):
                self.on_crop_selected(
                    image_rect
                )

        super().mouseReleaseEvent(event)




class ThemeToggle(QAbstractButton):
    """Compact sun/moon switch for the application theme."""

    def __init__(self, dark_mode=True, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(dark_mode)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Switch theme")
        self.setAccessibleName("Switch theme")
        self.setFixedSize(64, 32)

    def sizeHint(self):
        return QSize(64, 32)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(3, 4, -3, -4)
        dark = self.isChecked()

        track_color = QColor("#2D2F31" if dark else "#EEF0F4")
        border_color = QColor("#5F6368" if dark else "#C2C7D0")
        knob_color = QColor("#F8FAFC")
        icon_color = QColor("#4B5563" if not dark else "#1F2937")

        painter.setPen(QPen(border_color, 1))
        painter.setBrush(track_color)
        painter.drawRoundedRect(rect, 12, 12)

        knob_size = 22
        knob_x = rect.right() - knob_size - 1 if dark else rect.left() + 1
        knob_y = rect.top() + 1
        knob_rect = QRect(knob_x, knob_y, knob_size, knob_size)

        painter.setPen(QPen(QColor(0, 0, 0, 35), 1))
        painter.setBrush(knob_color)
        painter.drawEllipse(knob_rect)

        painter.setPen(QPen(icon_color, 1.3))
        if dark:
            self._draw_moon(painter, knob_rect)
        else:
            self._draw_sun(painter, knob_rect)

    def _draw_sun(self, painter, rect):
        center = rect.center()
        painter.drawEllipse(center, 3, 3)

        for dx, dy in ((0, -7), (0, 7), (-7, 0), (7, 0), (-5, -5), (5, -5), (-5, 5), (5, 5)):
            inner_x = center.x() + int(dx * 0.55)
            inner_y = center.y() + int(dy * 0.55)
            outer_x = center.x() + dx
            outer_y = center.y() + dy
            painter.drawLine(inner_x, inner_y, outer_x, outer_y)

    def _draw_moon(self, painter, rect):
        center = rect.center()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center.x() - 5, center.y() - 6, 12, 12)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#F8FAFC"))
        painter.drawEllipse(center.x() - 1, center.y() - 7, 12, 12)

# =====================================================
# ImagePanel
# =====================================================

class ImagePanel(QWidget):

    def __init__(
        self,
        title: str,
        on_crop_selected=None,
    ):
        super().__init__()

        layout = QVBoxLayout(self)

        layout.setSpacing(4)

        layout.setContentsMargins(
            2,
            2,
            2,
            2,
        )

        title_label = QLabel(title)

        title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title_label.setStyleSheet(
            """
            QLabel {
                font-weight: bold;
                font-size: 13px;
                padding: 4px;
                color: #E8EAED;
            }
            """
        )

        self.image_label = ImageLabel(
            on_crop_selected
        )

        layout.addWidget(title_label)

        layout.addWidget(
            self.image_label,
            stretch=1,
        )

    def set_image(
        self,
        cv_img,
    ):
        self.image_label.set_cv_image(
            cv_img
        )
