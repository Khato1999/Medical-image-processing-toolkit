"""
ActionsMixin
------------
Holds every method that actually touches image state: file I/O (open /
save / reset), the Phase 2-5 committed processing actions (basic,
enhancement, filters, edges, analysis, morphology, frequency,
registration), the live-preview slider handlers (brightness/contrast/
gamma, Canny thresholds, frequency radius), crop handling, and the
small shared helpers (_refresh_processed, _update_info, _commit_live_
adjustments, _reset_sliders_silently).

Mixed into MedicalImageToolkit alongside UIGroupsMixin in
main_window.py. Relies on widgets/attributes created there and in
ui_groups.py (self.base_image, self.processed_panel, self.brightness_
slider, etc).
"""

import os

import cv2
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, QRect

from . import dicom
from .processing import (basic, enhancement, filters, edges, analysis, measurements, frequency, registration, pipelines)

SUPPORTED_FILTER = "Images (*.jpg *.jpeg *.png *.bmp *.tif *.tiff *.dcm)"


class ActionsMixin:

    def show_histogram(self):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return

        import matplotlib.pyplot as plt

        hist = measurements.histogram(self.base_image)

        plt.figure("Histogram")
        plt.clf()

        plt.plot(hist)

        plt.title("Image Histogram")
        plt.xlabel("Pixel Intensity")
        plt.ylabel("Number of Pixels")

        plt.xlim([0, 255])

        plt.grid(True)

        plt.show()

    def show_dicom_metadata(self):

        if self.dicom_dataset is None:

            QMessageBox.information(
                self,
                "DICOM",
                "Current image is not a DICOM image.",
            )

            return

        info = dicom.metadata(self.dicom_dataset)

        text = ""

        for key, value in info.items():

            text += f"{key}: {value}\n"

        QMessageBox.information(
            self,
            "DICOM Metadata",
            text,
        )

    def toggle_theme(self):
        from .theme import DARK_THEME, LIGHT_THEME

        self.dark_mode = not self.dark_mode

        QApplication.instance().setStyleSheet(
            DARK_THEME if self.dark_mode else LIGHT_THEME
        )

        if hasattr(self, "theme_switch"):
            self.theme_switch.blockSignals(True)
            self.theme_switch.setChecked(self.dark_mode)
            self.theme_switch.blockSignals(False)
            self.theme_switch.update()

        self.statusBar().showMessage(
            "Dark mode enabled" if self.dark_mode else "Light mode enabled"
        )

    def load_reference_image(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Reference Image",
            "",
            SUPPORTED_FILTER,
        )

        if not path:
            return

        image = cv2.imread(
            path,
            cv2.IMREAD_UNCHANGED
        )

        if image is None:
            return

        self.registration_reference = image

        self.original_panel.set_image(
            image
        )

        self.statusBar().showMessage(
            "Reference image loaded"
        )

    def load_moving_image(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Moving Image",
            "",
            SUPPORTED_FILTER,
        )

        if not path:
            return

        image = cv2.imread(
            path,
            cv2.IMREAD_UNCHANGED
        )

        if image is None:
            return

        self.registration_moving = image

        self.processed_panel.set_image(
            image
        )

        self.statusBar().showMessage(
            "Moving image loaded"
        )

    def show_statistics(self):

        if self.base_image is None:
            return

        stats = measurements.roi_statistics(self.base_image)

        text = ""

        for key, value in stats.items():
            text += f"{key}: {value}\n"

        QMessageBox.information(
            self,
            "ROI Statistics",
            text,
        )

    def show_orb_matches(self):

        if (
            self.registration_reference is None
            or
            self.registration_moving is None
        ):
            return

        kp1, kp2, matches = (
            registration.orb_matches(
                self.registration_reference,
                self.registration_moving,
            )
        )

        matched = registration.draw_matches(
            self.registration_reference,
            self.registration_moving,
            kp1,
            kp2,
            matches,
        )

        self.base_image = matched
        self.processed_image = matched

        self._refresh_processed()

        self.statusBar().showMessage(
            f"{len(matches)} ORB matches found"
        )

    def show_registration_difference(self):

        if (
            self.registration_reference is None
            or
            self.processed_image is None
        ):
            return

        diff = registration.registration_difference(
            self.registration_reference,
            self.processed_image,
        )

        self.base_image = diff
        self.processed_image = diff

        self._refresh_processed()

        self.statusBar().showMessage(
            "Difference image generated"
        )

    def show_status(self, message, timeout=5000):
        """
        Display a message in the status bar.

        Parameters
        ----------
        message : str
            Message to display.

        timeout : int
            Display duration in milliseconds.
        """

        self.statusBar().showMessage(
            message,
            timeout
        )

    def show_about(self):

        QMessageBox.about(
            self,
            "About",

            """
    Medical Image Processing Toolkit

    Version 1.0

    Author: Khato

    Features

    â€¢ Enhancement
    â€¢ Filtering
    â€¢ FFT Processing
    â€¢ Edge Detection
    â€¢ Morphology
    â€¢ Registration
    â€¢ DICOM Support
    â€¢ ROI Measurements
            """
            )

    # ---------- file actions ----------

    def _update_undo_redo_state(self):
        if hasattr(self, "undo_action"):
            self.undo_action.setEnabled(bool(self.undo_stack))
        if hasattr(self, "redo_action"):
            self.redo_action.setEnabled(bool(self.redo_stack))

    def open_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", SUPPORTED_FILTER,)
        if not path:
            return
        extension = path.lower().split(".")[-1]

        if extension == "dcm":

            image, ds = dicom.load_dicom(path)

            self.dicom_dataset = ds

        else:

            image = cv2.imread(path, cv2.IMREAD_UNCHANGED)

            self.dicom_dataset = None

        if image is None:

            QMessageBox.warning(
                self,
                "Error",
                "Could not load image.",
            )

            return

        self.original_image = image
        self.base_image = image.copy()
        self.processed_image = self.base_image.copy()
        self.fft_mode = False
        self.current_fft = None
        self.undo_stack = []
        self.redo_stack = []
        self._deactivate_crop()
        self._reset_sliders_silently()


        self.original_panel.set_image(self.original_image)
        self.processed_panel.set_image(self.processed_image)
        self._update_info(image)
        self._update_undo_redo_state()
        self.statusBar().showMessage(f"Loaded: {os.path.basename(path)}")

    def reset_image(self):
        if self.original_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._push_undo_state()
        self.base_image = self.original_image.copy()
        self.processed_image = self.base_image.copy()
        self.current_fft = None
        self.fft_mode = False

        self._deactivate_crop()
        self._reset_sliders_silently()
        self._refresh_processed()
        self.statusBar().showMessage("Processed image reset to original")

    def save_image(self):
        if self.processed_image is None:
            QMessageBox.information(self, "No image", "Load an image first.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Image", "",
            "PNG (*.png);;JPEG (*.jpg);;BMP (*.bmp);;TIFF (*.tif)"
        )
        if not path:
            return
        try:
            saved = cv2.imwrite(path, self.processed_image)
        except cv2.error as exc:
            QMessageBox.warning(self, "Save failed", str(exc))
            return

        if not saved:
            QMessageBox.warning(self, "Save failed", "OpenCV could not write the selected file.")
            return

        self.statusBar().showMessage(f"Saved: {path}")

    def _push_undo_state(self):

        if self.base_image is None:
            return

        self.undo_stack.append(
            self.base_image.copy()
        )

        # any new action invalidates redo history
        self.redo_stack.clear()

        # optional limit
        if len(self.undo_stack) > 20:
            self.undo_stack.pop(0)

        self._update_undo_redo_state()

    def undo(self):

        if not self.undo_stack:

            self.statusBar().showMessage(
                "Nothing to undo"
            )

            return

        self.redo_stack.append(
            self.base_image.copy()
        )

        self.base_image = (
            self.undo_stack.pop()
        )

        self.processed_image = (
            self.base_image.copy()
        )

        self._refresh_processed()
        self._update_undo_redo_state()

        self.statusBar().showMessage(
            "Undo"
        )

    def redo(self):

        if not self.redo_stack:

            self.statusBar().showMessage(
                "Nothing to redo"
            )

            return

        self.undo_stack.append(
            self.base_image.copy()
        )

        self.base_image = (
            self.redo_stack.pop()
        )

        self.processed_image = (
            self.base_image.copy()
        )

        self._refresh_processed()
        self._update_undo_redo_state()

        self.statusBar().showMessage(
            "Redo"
        )

    # ---------- Phase 2: committed processing actions ----------
    # Each of these commits any pending live brightness/contrast/gamma
    # preview into base_image first, then performs its own transform
    # (delegated to toolkit.processing.basic) on base_image, then
    # republishes base_image as the new processed_image.

    def apply_grayscale(self):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._commit_live_adjustments()
        if self.base_image.ndim == 3:
            self.base_image = basic.to_grayscale(self.base_image)
            self.processed_image = self.base_image.copy()
            self._refresh_processed()
            self.statusBar().showMessage("Converted to grayscale")
        else:
            self.statusBar().showMessage("Image is already grayscale")

    def apply_resize(self, pct):
        if self.original_image is None or self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._commit_live_adjustments()
        self.base_image = basic.resize_to_percent(
            self.base_image, self.original_image.shape, pct
        )
        self.processed_image = self.base_image.copy()
        self._refresh_processed()
        h, w = self.base_image.shape[:2]
        self.statusBar().showMessage(f"Resized to {pct}% ({w} x {h})")
    def apply_resize_current(self, pct):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._commit_live_adjustments()
        self.base_image = basic.resize_current_percent(self.base_image, pct)
        self.processed_image = self.base_image.copy()
        self._refresh_processed()
        h, w = self.base_image.shape[:2]
        self.statusBar().showMessage(f"Resized current image to {pct}% ({w} x {h})")

    def apply_fit_long_edge(self, size=512):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._commit_live_adjustments()
        self.base_image = basic.fit_long_edge(self.base_image, size)
        self.processed_image = self.base_image.copy()
        self._refresh_processed()
        h, w = self.base_image.shape[:2]
        self.statusBar().showMessage(f"Fit longest edge to {size}px ({w} x {h})")

    def apply_rotate_free(self, angle):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._commit_live_adjustments()
        self.base_image = basic.rotate_free(self.base_image, angle)
        self.processed_image = self.base_image.copy()
        self._refresh_processed()
        self.statusBar().showMessage(f"Rotated {angle} degrees")

    def apply_invert(self):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._commit_live_adjustments()
        self.base_image = basic.invert(self.base_image)
        self.processed_image = self.base_image.copy()
        self._refresh_processed()
        self.statusBar().showMessage("Inverted image intensities")

    def apply_normalize_intensity(self):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._commit_live_adjustments()
        self.base_image = basic.normalize_intensity(self.base_image)
        self.processed_image = self.base_image.copy()
        self._refresh_processed()
        self.statusBar().showMessage("Normalized intensities to 0-255")

    def apply_center_crop_square(self):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._commit_live_adjustments()
        self.base_image = basic.center_crop_square(self.base_image)
        self.processed_image = self.base_image.copy()
        self._refresh_processed()
        h, w = self.base_image.shape[:2]
        self.statusBar().showMessage(f"Center-cropped square ({w} x {h})")


    def apply_rotate(self, angle):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._commit_live_adjustments()
        self.base_image = basic.rotate(self.base_image, angle)
        self.processed_image = self.base_image.copy()
        self._refresh_processed()
        self.statusBar().showMessage(f"Rotated {angle}Â°")

    def apply_flip(self, mode):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._commit_live_adjustments()
        self.base_image = basic.flip(self.base_image, mode)
        self.processed_image = self.base_image.copy()
        self._refresh_processed()
        self.statusBar().showMessage(
            f"Flipped {'horizontally' if mode == 'h' else 'vertically'}"
        )

    def apply_threshold(self):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return

        self._commit_live_adjustments()

        self.base_image = analysis.threshold(self.base_image)

        self.processed_image = self.base_image.copy()

        self._refresh_processed()

        self.statusBar().showMessage("Threshold applied")

    def apply_adaptive_threshold(self):
        if self.base_image is None:
            return

        self._commit_live_adjustments()

        self.base_image = analysis.adaptive_threshold(self.base_image)

        self.processed_image = self.base_image.copy()
        self._refresh_processed()

        self.statusBar().showMessage("Adaptive threshold applied")

    def apply_otsu(self):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return

        self._commit_live_adjustments()

        self.base_image = analysis.otsu(self.base_image)
        self.processed_image = self.base_image.copy()

        self._refresh_processed()
        self.statusBar().showMessage("Otsu threshold applied")

    def _morphology_params(self):
        ksize = self.morph_kernel_spin.value()
        iterations = self.morph_iterations_spin.value()
        shape = self.morph_shape_combo.currentText().lower()
        return ksize, iterations, shape

    def _apply_morphology(self, transform, label):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return

        ksize, iterations, shape = self._morphology_params()
        self._commit_live_adjustments()
        self.base_image = transform(self.base_image, ksize, iterations, shape)
        self.processed_image = self.base_image.copy()
        self._refresh_processed()
        self.statusBar().showMessage(
            f"{label} applied (kernel {ksize}, {iterations} iteration(s), {shape})"
        )

    def apply_erosion(self):
        self._apply_morphology(analysis.erode, "Erosion")

    def apply_dilation(self):
        self._apply_morphology(analysis.dilate, "Dilation")

    def apply_opening(self):
        self._apply_morphology(analysis.opening, "Opening")

    def apply_closing(self):
        self._apply_morphology(analysis.closing, "Closing")

    def apply_morphological_gradient(self):
        self._apply_morphology(analysis.morphological_gradient, "Morphological gradient")

    def apply_top_hat(self):
        self._apply_morphology(analysis.top_hat, "Top-hat")

    def apply_black_hat(self):
        self._apply_morphology(analysis.black_hat, "Black-hat")

    def apply_opening_reconstruction(self):
        self._apply_morphology(analysis.opening_by_reconstruction, "Opening by reconstruction")

    def apply_closing_reconstruction(self):
        self._apply_morphology(analysis.closing_by_reconstruction, "Closing by reconstruction")
    def apply_connected_components(self):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return

        self._commit_live_adjustments()

        self.base_image = analysis.connected_components(self.base_image)
        self.processed_image = self.base_image.copy()

        self._refresh_processed()
        self.statusBar().showMessage("Connected components detected")

    def apply_fft_spectrum(self):

        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return

        self._commit_live_adjustments()

        # Store REAL FFT
        self.current_fft = frequency.compute_fft(self.base_image)

        # Display spectrum image
        self.processed_image = frequency.fft_spectrum(self.base_image)

        self._refresh_processed()
        self.statusBar().showMessage("FFT spectrum generated")
        self.fft_mode = True


    def apply_inverse_fft(self):

        if self.current_fft is None:

            self.statusBar().showMessage("Generate FFT first")

            return

        self.processed_image = (
            frequency.inverse_fft(
                self.current_fft
            )
        )

        self._refresh_processed()

        self.statusBar().showMessage(
            "Inverse FFT completed"
        )

    def apply_low_pass(self):

        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return

        self.current_frequency_mode = "low"

        self._apply_frequency_preview()

        self.statusBar().showMessage(
            "Low-pass filter active. Adjust radius slider."
        )

    def apply_high_pass(self):

        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return

        self.current_frequency_mode = "high"

        self._apply_frequency_preview()

        self.statusBar().showMessage(
            "High-pass filter active. Adjust radius slider."
        )

    def apply_band_pass(self):

        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return

        self.current_frequency_mode = "band_pass"

        self._apply_frequency_preview()

        self.statusBar().showMessage(
            "Band-pass filter active. Adjust radius slider."
        )

    def apply_band_stop(self):

        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return

        self.current_frequency_mode = "band_stop"

        self._apply_frequency_preview()

        self.statusBar().showMessage(
            "Band-stop filter active. Adjust radius slider."
        )

    def apply_ecc_registration(self):

        if (
            self.registration_reference is None
            or
            self.registration_moving is None
        ):
            return

        aligned, matrix, cc = (
            registration.register_ecc(
                self.registration_reference,
                self.registration_moving,
            )
        )

        self.base_image = aligned
        self.processed_image = aligned

        self._refresh_processed()

        self.statusBar().showMessage(
            f"ECC correlation: {cc:.4f}"
        )

    def apply_affine_registration(self):

        if (
            self.registration_reference is None
            or
            self.registration_moving is None
        ):
            return

        aligned = registration.affine_registration(
            self.registration_reference,
            self.registration_moving,
        )

        self.base_image = aligned
        self.processed_image = aligned

        self._refresh_processed()

        self.statusBar().showMessage(
            "Affine registration completed"
        )

    def apply_perspective_registration(self):

        if (
            self.registration_reference is None
            or
            self.registration_moving is None
        ):
            return

        aligned = registration.perspective_registration(
            self.registration_reference,
            self.registration_moving,
        )

        self.base_image = aligned
        self.processed_image = aligned

        self._refresh_processed()

        self.statusBar().showMessage(
            "Perspective registration completed"
        )

    def _apply_frequency_preview(self):

        if self.base_image is None:
            return

        if self.current_frequency_mode is None:
            return

        radius = self.frequency_radius_slider.value()

        if self.current_frequency_mode == "low":

            result = frequency.low_pass(
                self.base_image,
                radius
            )

        elif self.current_frequency_mode == "high":

            result = frequency.high_pass(
                self.base_image,
                radius
            )

        elif self.current_frequency_mode == "band_pass":

            result = frequency.band_pass(
                self.base_image,
                radius,
                radius * 2
            )

        elif self.current_frequency_mode == "band_stop":

            result = frequency.band_stop(
                self.base_image,
                radius,
                radius * 2
            )

        else:
            return

        self.processed_image = result

        self._refresh_processed()

    def _on_frequency_radius_changed(self, value):

        self.frequency_radius_label.setText(
            f"Radius: {value}"
        )

        self._apply_frequency_preview()


    
    def toggle_crop(self):
        if self.base_image is None:
            self.statusBar().showMessage("Load an image first")
            return
        label = self.processed_panel.image_label
        if not label.crop_active and not self.fft_mode:
            # entering crop mode: make sure what's on screen (and therefore
            # what the drag will crop) is the committed base image.
            # Skipped in fft_mode: while viewing the FFT spectrum,
            # processed_image holds the spectrum visualization, not real
            # image data â€” committing here would overwrite base_image with
            # spectrum pixels, and would also wipe current_fft/fft_mode
            # (via _commit_live_adjustments) before the crop drag even
            # starts, breaking the frequency-domain masking below.
            self._commit_live_adjustments()
        label.crop_active = not label.crop_active
        self.crop_btn.setText("Cancel Crop" if label.crop_active else "Crop Selection")
        label.setCursor(
            Qt.CursorShape.CrossCursor if label.crop_active else Qt.CursorShape.ArrowCursor
        )
        if label.crop_active:
            self.statusBar().showMessage("Drag a rectangle on the Processed Image to crop")
        else:
            self.statusBar().showMessage("Crop cancelled")

    def _on_crop_selected(self, rect):

        if self.base_image is None:
            return

        if self.fft_mode:

            x1 = rect.left()
            y1 = rect.top()

            x2 = rect.right()
            y2 = rect.bottom()

            self.current_fft[y1:y2, x1:x2] = 0

            self.processed_image = (
                frequency.spectrum_from_fft(
                    self.current_fft
                )
            )

            self._refresh_processed()

            return

        self.base_image = basic.crop(
            self.base_image,
            rect.left(),
            rect.top(),
            rect.right(),
            rect.bottom()
        )

        self.processed_image = self.base_image.copy()

        self._deactivate_crop()

        self._refresh_processed()

   
    
    def _deactivate_crop(self):
        label = self.processed_panel.image_label
        label.crop_active = False
        label.setCursor(Qt.CursorShape.ArrowCursor)
        self.crop_btn.setText("Crop Selection")

    # ---------- Phase 3: enhancement ----------

    def _on_brightness_changed(self, value):
        self.brightness_label.setText(f"Brightness: {value}")
        self._apply_live_adjustments()

    def _on_contrast_changed(self, value):
        self.contrast_label.setText(f"Contrast: {value / 100:.2f}")
        self._apply_live_adjustments()

    def _on_gamma_changed(self, value):
        self.gamma_label.setText(f"Gamma: {value / 100:.2f}")
        self._apply_live_adjustments()

    def _apply_live_adjustments(self):
        """Recompute processed_image = f(base_image) for the current
        slider values, WITHOUT touching base_image. This is what makes
        dragging a slider back and forth non-destructive."""
        if self.base_image is None:
            return
        self.processed_image = enhancement.adjust_brightness_contrast_gamma(
            self.base_image,
            brightness=self.brightness_slider.value(),
            contrast=self.contrast_slider.value() / 100.0,
            gamma=self.gamma_slider.value() / 100.0,
        )
        self._refresh_processed()

    def _commit_live_adjustments(self):
        """Fold the current slider preview permanently into base_image and
        put the sliders back to their neutral position, without changing
        what's on screen."""
        if self.base_image is None or self.processed_image is None:
            return
        self._push_undo_state()
        self.base_image = self.processed_image.copy()
        self._reset_sliders_silently()
        # any cached FFT no longer matches base_image once it's been
        # edited â€” force the user to regenerate it before inverting
        self.current_fft = None
        self.fft_mode = False

    def _reset_sliders_silently(self):
        for slider in (self.brightness_slider, self.contrast_slider, self.gamma_slider):
            slider.blockSignals(True)
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(100)
        self.gamma_slider.setValue(100)
        for slider in (self.brightness_slider, self.contrast_slider, self.gamma_slider):
            slider.blockSignals(False)
        self.brightness_label.setText("Brightness: 0")
        self.contrast_label.setText("Contrast: 1.00")
        self.gamma_label.setText("Gamma: 1.00")

    def apply_histogram_equalization(self):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._commit_live_adjustments()
        self.base_image = enhancement.histogram_equalization(self.base_image)
        self.processed_image = self.base_image.copy()
        self._refresh_processed()
        self.statusBar().showMessage("Histogram equalization applied")

    def apply_clahe(self):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._commit_live_adjustments()
        self.base_image = enhancement.clahe(self.base_image)
        self.processed_image = self.base_image.copy()
        self._refresh_processed()
        self.statusBar().showMessage("CLAHE applied (clip limit 2.0, tile 8x8)")

    # ---------- Phase 4: filters ----------
    # Same commit-then-transform pattern as the Phase 3 one-shot actions.

    def apply_gaussian_blur(self, ksize):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._commit_live_adjustments()
        self.base_image = filters.gaussian_blur(self.base_image, ksize)
        self.processed_image = self.base_image.copy()
        self._refresh_processed()
        self.statusBar().showMessage(f"Gaussian blur {ksize}x{ksize} applied")

    def apply_median_blur(self):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._commit_live_adjustments()
        self.base_image = filters.median_blur(self.base_image)
        self.processed_image = self.base_image.copy()
        self._refresh_processed()
        self.statusBar().showMessage("Median blur (5x5) applied")

    def apply_bilateral_filter(self):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._commit_live_adjustments()
        self.base_image = filters.bilateral_filter(self.base_image)
        self.processed_image = self.base_image.copy()
        self._refresh_processed()
        self.statusBar().showMessage("Bilateral filter applied (d=9, sigma=75)")

    def apply_average_blur(self):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._commit_live_adjustments()
        self.base_image = filters.average_blur(self.base_image)
        self.processed_image = self.base_image.copy()
        self._refresh_processed()
        self.statusBar().showMessage("Average blur (5x5) applied")

    def apply_sharpen(self):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._commit_live_adjustments()
        self.base_image = filters.sharpen(self.base_image)
        self.processed_image = self.base_image.copy()
        self._refresh_processed()
        self.statusBar().showMessage("Sharpen filter applied")

    def apply_emboss(self):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._commit_live_adjustments()
        self.base_image = filters.emboss(self.base_image)
        self.processed_image = self.base_image.copy()
        self._refresh_processed()
        self.statusBar().showMessage("Emboss filter applied")

    # ---------- Phase 5: edge detection ----------
    # Sobel / Scharr / Laplacian are one-shot committed operations, same
    # pattern as the filters above. Canny is the odd one out: it has two
    # threshold sliders, so it gets a live, non-destructive preview
    # (same pattern as the Phase 3 enhancement sliders) instead of being
    # baked in immediately.

    def apply_sobel(self):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._commit_live_adjustments()
        self.base_image = edges.sobel(self.base_image)
        self.processed_image = self.base_image.copy()
        self._refresh_processed()
        self.statusBar().showMessage("Sobel edge detection applied")

    def apply_scharr(self):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._commit_live_adjustments()
        self.base_image = edges.scharr(self.base_image)
        self.processed_image = self.base_image.copy()
        self._refresh_processed()
        self.statusBar().showMessage("Scharr edge detection applied")

    def apply_laplacian(self):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        self._commit_live_adjustments()
        self.base_image = edges.laplacian(self.base_image)
        self.processed_image = self.base_image.copy()
        self._refresh_processed()
        self.statusBar().showMessage("Laplacian edge detection applied")

    def apply_canny(self):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return
        # fold in any pending brightness/contrast/gamma preview so Canny
        # runs on what the user is actually looking at
        self._commit_live_adjustments()
        self._apply_canny_preview()
        self.statusBar().showMessage(
            "Canny edge detection applied â€” fine-tune with the threshold sliders"
        )

    def _on_canny_threshold_changed(self, _value):
        self.canny_t1_label.setText(f"Threshold 1: {self.canny_t1_slider.value()}")
        self.canny_t2_label.setText(f"Threshold 2: {self.canny_t2_slider.value()}")
        self._apply_canny_preview()

    def _apply_canny_preview(self):
        """Recompute processed_image = Canny(base_image) for the current
        threshold values, WITHOUT touching base_image â€” mirrors
        _apply_live_adjustments so dragging the sliders back and forth
        stays non-destructive."""
        if self.base_image is None:
            return
        self.processed_image = edges.canny(
            self.base_image, self.canny_t1_slider.value(), self.canny_t2_slider.value()
        )
        self._refresh_processed()

    def _apply_pipeline(self, transform, message):
        if self.base_image is None:
            self.statusBar().showMessage("No image loaded")
            return

        self._commit_live_adjustments()
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        try:
            result = transform(self.base_image)
        except Exception as exc:
            QMessageBox.warning(self, "Pipeline failed", str(exc))
            self.statusBar().showMessage("Pipeline failed")
            return
        finally:
            QApplication.restoreOverrideCursor()

        self.base_image = result
        self.processed_image = self.base_image.copy()
        self.current_fft = None
        self.fft_mode = False
        self._refresh_processed()
        self.statusBar().showMessage(message)

    def apply_pipeline_clean_contrast(self):
        self._apply_pipeline(
            pipelines.clean_contrast_detail,
            "Pipeline applied: clean, contrast, and detail",
        )

    def apply_pipeline_soft_tissue(self):
        self._apply_pipeline(
            pipelines.soft_tissue_window,
            "Pipeline applied: soft tissue review",
        )

    def apply_pipeline_segmentation(self):
        self._apply_pipeline(
            pipelines.segmentation_ready,
            "Pipeline applied: segmentation-ready mask",
        )

    def apply_pipeline_edge_review(self):
        self._apply_pipeline(
            pipelines.edge_review,
            "Pipeline applied: edge review",
        )
    # ---------- helpers ----------

    def _refresh_processed(self):
        self.processed_panel.set_image(self.processed_image)
        self._update_info(self.processed_image)

    def _update_info(self, img):
        h, w = img.shape[:2]
        channels = 1 if img.ndim == 2 else img.shape[2]
        img_type = ("Grayscale" if img.ndim ==2 else f"Color ({channels} channels)")
        self.info_labels["Image Type"].setText(f"Type: {img_type}")

        self.info_labels["Width"].setText(f"Width: {w}px")
        self.info_labels["Height"].setText(f"Height: {h}px")
        self.info_labels["Resolution"].setText(f"Resolution: {w} x {h}")
        self.info_labels["Channels"].setText(f"Channels: {channels}")






