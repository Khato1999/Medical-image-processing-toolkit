"""
UIGroupsMixin
-------------
Holds every `_build_*_group()` method â€” the widgets/layouts for each
control panel (Processing, Enhancement, Filters, Edge Detection,
Morphology, Analysis, DICOM, Frequency, Registration). These are pure
UI-construction helpers: they build a QGroupBox, wire button/slider
signals to handlers defined in ActionsMixin, and return the group.

Mixed into MedicalImageToolkit alongside ActionsMixin in main_window.py.
"""

from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider, QSpinBox, QComboBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt


class UIGroupsMixin:

    def _build_processing_group(self):
        group = QGroupBox("Processing")
        layout = QVBoxLayout(group)

        row = QHBoxLayout()
        gray_btn = QPushButton(QIcon("icons/grayscale.png"), "Grayscale")
        gray_btn.clicked.connect(self.apply_grayscale)
        row.addWidget(gray_btn)

        invert_btn = QPushButton("Invert")
        invert_btn.clicked.connect(self.apply_invert)
        row.addWidget(invert_btn)

        normalize_btn = QPushButton("Normalize")
        normalize_btn.clicked.connect(self.apply_normalize_intensity)
        row.addWidget(normalize_btn)
        layout.addLayout(row)

        row = QHBoxLayout()
        row.addWidget(QLabel("Resize current:"))
        for pct in (50, 75, 125, 150):
            btn = QPushButton(f"{pct}%")
            btn.clicked.connect(lambda _, p=pct: self.apply_resize_current(p))
            row.addWidget(btn)
        layout.addLayout(row)

        row = QHBoxLayout()
        row.addWidget(QLabel("Custom:"))
        self.resize_percent_spin = QSpinBox()
        self.resize_percent_spin.setRange(5, 400)
        self.resize_percent_spin.setValue(100)
        self.resize_percent_spin.setSuffix("%")
        row.addWidget(self.resize_percent_spin)

        resize_custom_btn = QPushButton("Apply")
        resize_custom_btn.clicked.connect(
            lambda: self.apply_resize_current(self.resize_percent_spin.value())
        )
        row.addWidget(resize_custom_btn)

        fit_512_btn = QPushButton("Fit 512px")
        fit_512_btn.clicked.connect(lambda: self.apply_fit_long_edge(512))
        row.addWidget(fit_512_btn)
        layout.addLayout(row)

        row = QHBoxLayout()
        row.addWidget(QLabel("Rotate:"))
        rotate_left_btn = QPushButton("Left 90")
        rotate_left_btn.clicked.connect(lambda: self.apply_rotate(270))
        row.addWidget(rotate_left_btn)

        rotate_180_btn = QPushButton("180")
        rotate_180_btn.clicked.connect(lambda: self.apply_rotate(180))
        row.addWidget(rotate_180_btn)

        rotate_right_btn = QPushButton("Right 90")
        rotate_right_btn.clicked.connect(lambda: self.apply_rotate(90))
        row.addWidget(rotate_right_btn)
        layout.addLayout(row)

        row = QHBoxLayout()
        row.addWidget(QLabel("Angle:"))
        self.rotate_angle_spin = QSpinBox()
        self.rotate_angle_spin.setRange(-180, 180)
        self.rotate_angle_spin.setValue(0)
        self.rotate_angle_spin.setSuffix(" deg")
        row.addWidget(self.rotate_angle_spin)

        rotate_custom_btn = QPushButton("Apply")
        rotate_custom_btn.clicked.connect(
            lambda: self.apply_rotate_free(self.rotate_angle_spin.value())
        )
        row.addWidget(rotate_custom_btn)
        layout.addLayout(row)

        row = QHBoxLayout()
        row.addWidget(QLabel("Flip:"))
        flip_h_btn = QPushButton("Horizontal")
        flip_h_btn.clicked.connect(lambda: self.apply_flip("h"))
        row.addWidget(flip_h_btn)

        flip_v_btn = QPushButton("Vertical")
        flip_v_btn.clicked.connect(lambda: self.apply_flip("v"))
        row.addWidget(flip_v_btn)
        layout.addLayout(row)

        row = QHBoxLayout()
        self.crop_btn = QPushButton("Crop Selection")
        self.crop_btn.clicked.connect(self.toggle_crop)
        row.addWidget(self.crop_btn)

        square_crop_btn = QPushButton("Center Square")
        square_crop_btn.clicked.connect(self.apply_center_crop_square)
        row.addWidget(square_crop_btn)
        layout.addLayout(row)

        return group

    def _build_enhancement_group(self):
        group = QGroupBox("Enhancement")
        layout = QVBoxLayout(group)

        # Brightness: -100..100, default 0
        row = QHBoxLayout()
        self.brightness_label = QLabel("Brightness: 0")
        self.brightness_label.setFixedWidth(140)
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self._on_brightness_changed)
        row.addWidget(self.brightness_label)
        row.addWidget(self.brightness_slider)
        layout.addLayout(row)

        # Contrast: slider int 50..200 represents 0.50..2.00, default 100 -> 1.00
        row = QHBoxLayout()
        self.contrast_label = QLabel("Contrast: 1.00")
        self.contrast_label.setFixedWidth(140)
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(50, 200)
        self.contrast_slider.setValue(100)
        self.contrast_slider.valueChanged.connect(self._on_contrast_changed)
        row.addWidget(self.contrast_label)
        row.addWidget(self.contrast_slider)
        layout.addLayout(row)

        # Gamma: slider int 10..300 represents 0.10..3.00, default 100 -> 1.00
        row = QHBoxLayout()
        self.gamma_label = QLabel("Gamma: 1.00")
        self.gamma_label.setFixedWidth(140)
        self.gamma_slider = QSlider(Qt.Orientation.Horizontal)
        self.gamma_slider.setRange(10, 300)
        self.gamma_slider.setValue(100)
        self.gamma_slider.valueChanged.connect(self._on_gamma_changed)
        row.addWidget(self.gamma_label)
        row.addWidget(self.gamma_slider)
        layout.addLayout(row)

        # Histogram equalization / CLAHE (committed, one-shot operations)
        row = QHBoxLayout()
        hist_btn = QPushButton("Histogram Equalization")
        hist_btn.clicked.connect(self.apply_histogram_equalization)
        row.addWidget(hist_btn)
        clahe_btn = QPushButton("CLAHE")
        clahe_btn.clicked.connect(self.apply_clahe)
        row.addWidget(clahe_btn)
        layout.addLayout(row)

        return group

    def _build_filters_group(self):
        group = QGroupBox("Filters")
        layout = QVBoxLayout(group)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Gaussian Blur:"))
        for ksize in (3, 5, 7):
            btn = QPushButton(f"{ksize}x{ksize}")
            btn.clicked.connect(lambda _, k=ksize: self.apply_gaussian_blur(k))
            row1.addWidget(btn)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        median_btn = QPushButton("Median Blur")
        median_btn.clicked.connect(self.apply_median_blur)
        row2.addWidget(median_btn)
        bilateral_btn = QPushButton("Bilateral Filter")
        bilateral_btn.clicked.connect(self.apply_bilateral_filter)
        row2.addWidget(bilateral_btn)
        average_btn = QPushButton("Average Blur")
        average_btn.clicked.connect(self.apply_average_blur)
        row2.addWidget(average_btn)
        layout.addLayout(row2)

        row3 = QHBoxLayout()
        sharpen_btn = QPushButton("Sharpen")
        sharpen_btn.clicked.connect(self.apply_sharpen)
        row3.addWidget(sharpen_btn)
        emboss_btn = QPushButton("Emboss")
        emboss_btn.clicked.connect(self.apply_emboss)
        row3.addWidget(emboss_btn)
        layout.addLayout(row3)

        return group

    def _build_pipeline_group(self):
        group = QGroupBox("Professional Pipeline")
        layout = QVBoxLayout(group)

        clean_btn = QPushButton("Clean + Contrast + Detail")
        clean_btn.clicked.connect(self.apply_pipeline_clean_contrast)
        layout.addWidget(clean_btn)

        soft_tissue_btn = QPushButton("Soft Tissue Review")
        soft_tissue_btn.clicked.connect(self.apply_pipeline_soft_tissue)
        layout.addWidget(soft_tissue_btn)

        segmentation_btn = QPushButton("Segmentation Ready Mask")
        segmentation_btn.clicked.connect(self.apply_pipeline_segmentation)
        layout.addWidget(segmentation_btn)

        edge_btn = QPushButton("Edge Review")
        edge_btn.clicked.connect(self.apply_pipeline_edge_review)
        layout.addWidget(edge_btn)

        return group
    def _build_edge_detection_group(self):
        group = QGroupBox("Edge Detection")
        layout = QVBoxLayout(group)

        row1 = QHBoxLayout()
        sobel_btn = QPushButton("Sobel")
        sobel_btn.clicked.connect(self.apply_sobel)
        row1.addWidget(sobel_btn)
        scharr_btn = QPushButton("Scharr")
        scharr_btn.clicked.connect(self.apply_scharr)
        row1.addWidget(scharr_btn)
        laplacian_btn = QPushButton("Laplacian")
        laplacian_btn.clicked.connect(self.apply_laplacian)
        row1.addWidget(laplacian_btn)
        canny_btn = QPushButton("Canny")
        canny_btn.clicked.connect(self.apply_canny)
        row1.addWidget(canny_btn)
        layout.addLayout(row1)

        # Canny thresholds: live preview, recomputed straight from
        # base_image every time either slider moves (same non-destructive
        # pattern as the Phase 3 enhancement sliders)
        row2 = QHBoxLayout()
        self.canny_t1_label = QLabel("Threshold 1: 50")
        self.canny_t1_label.setFixedWidth(140)
        self.canny_t1_slider = QSlider(Qt.Orientation.Horizontal)
        self.canny_t1_slider.setRange(0, 500)
        self.canny_t1_slider.setValue(50)
        self.canny_t1_slider.valueChanged.connect(self._on_canny_threshold_changed)
        row2.addWidget(self.canny_t1_label)
        row2.addWidget(self.canny_t1_slider)
        layout.addLayout(row2)

        row3 = QHBoxLayout()
        self.canny_t2_label = QLabel("Threshold 2: 150")
        self.canny_t2_label.setFixedWidth(140)
        self.canny_t2_slider = QSlider(Qt.Orientation.Horizontal)
        self.canny_t2_slider.setRange(0, 500)
        self.canny_t2_slider.setValue(150)
        self.canny_t2_slider.valueChanged.connect(self._on_canny_threshold_changed)
        row3.addWidget(self.canny_t2_label)
        row3.addWidget(self.canny_t2_slider)
        layout.addLayout(row3)

        return group

    def _build_morphology_group(self):

        group = QGroupBox("Morphology")
        layout = QVBoxLayout(group)

        params_row = QHBoxLayout()
        params_row.addWidget(QLabel("Kernel:"))
        self.morph_kernel_spin = QSpinBox()
        self.morph_kernel_spin.setRange(1, 31)
        self.morph_kernel_spin.setSingleStep(2)
        self.morph_kernel_spin.setValue(3)
        self.morph_kernel_spin.setSuffix(" px")
        params_row.addWidget(self.morph_kernel_spin)

        params_row.addWidget(QLabel("Iterations:"))
        self.morph_iterations_spin = QSpinBox()
        self.morph_iterations_spin.setRange(1, 20)
        self.morph_iterations_spin.setValue(1)
        params_row.addWidget(self.morph_iterations_spin)
        layout.addLayout(params_row)

        shape_row = QHBoxLayout()
        shape_row.addWidget(QLabel("Shape:"))
        self.morph_shape_combo = QComboBox()
        self.morph_shape_combo.addItems(["Rect", "Ellipse", "Cross"])
        shape_row.addWidget(self.morph_shape_combo)
        layout.addLayout(shape_row)

        row = QHBoxLayout()
        erosion_btn = QPushButton("Erode")
        erosion_btn.clicked.connect(self.apply_erosion)
        row.addWidget(erosion_btn)

        dilation_btn = QPushButton("Dilate")
        dilation_btn.clicked.connect(self.apply_dilation)
        row.addWidget(dilation_btn)
        layout.addLayout(row)

        row = QHBoxLayout()
        opening_btn = QPushButton("Open")
        opening_btn.clicked.connect(self.apply_opening)
        row.addWidget(opening_btn)

        closing_btn = QPushButton("Close")
        closing_btn.clicked.connect(self.apply_closing)
        row.addWidget(closing_btn)
        layout.addLayout(row)

        row = QHBoxLayout()
        gradient_btn = QPushButton("Gradient")
        gradient_btn.clicked.connect(self.apply_morphological_gradient)
        row.addWidget(gradient_btn)

        top_hat_btn = QPushButton("Top-hat")
        top_hat_btn.clicked.connect(self.apply_top_hat)
        row.addWidget(top_hat_btn)

        black_hat_btn = QPushButton("Black-hat")
        black_hat_btn.clicked.connect(self.apply_black_hat)
        row.addWidget(black_hat_btn)
        layout.addLayout(row)

        row = QHBoxLayout()
        opening_recon_btn = QPushButton("Open Recon")
        opening_recon_btn.clicked.connect(self.apply_opening_reconstruction)
        row.addWidget(opening_recon_btn)

        closing_recon_btn = QPushButton("Close Recon")
        closing_recon_btn.clicked.connect(self.apply_closing_reconstruction)
        row.addWidget(closing_recon_btn)
        layout.addLayout(row)

        return group
    def _build_analysis_group(self):
        group = QGroupBox("Image analysis")
        layout = QHBoxLayout(group)

        threshold_btn = QPushButton("Threshold")
        threshold_btn.clicked.connect(self.apply_threshold)
        layout.addWidget(threshold_btn)

        adaptive_btn = QPushButton("Adaptive")
        adaptive_btn.clicked.connect(self.apply_adaptive_threshold)
        layout.addWidget(adaptive_btn)

        otsu_btn = QPushButton("Otsu")
        otsu_btn.clicked.connect(self.apply_otsu)
        layout.addWidget(otsu_btn)

        stats_btn = QPushButton("ROI Statistics")
        stats_btn.clicked.connect(self.show_statistics)
        layout.addWidget(stats_btn)

        hist_btn = QPushButton("Histogram")
        hist_btn.clicked.connect(self.show_histogram)

        layout.addWidget(hist_btn)
        return group

    def _build_dicom_group(self):

        group = QGroupBox("DICOM")

        layout = QVBoxLayout(group)

        btn = QPushButton("Show Metadata")

        btn.clicked.connect(self.show_dicom_metadata)

        layout.addWidget(btn)

        return group

    def _build_frequency_group(self):

        group = QGroupBox("Frequency Processing (FFT)")

        layout = QVBoxLayout(group)

        fft_btn = QPushButton("FFT Spectrum")
        fft_btn.clicked.connect(self.apply_fft_spectrum)

        inverse_btn = QPushButton("Inverse FFT")
        inverse_btn.clicked.connect(self.apply_inverse_fft)

        low_btn = QPushButton("Low Pass Filter")
        low_btn.clicked.connect(self.apply_low_pass)

        high_btn = QPushButton("High Pass Filter")
        high_btn.clicked.connect(self.apply_high_pass)

        band_pass_btn = QPushButton("Band Pass Filter")
        band_pass_btn.clicked.connect(self.apply_band_pass)

        band_stop_btn = QPushButton("Band Stop Filter")
        band_stop_btn.clicked.connect(self.apply_band_stop)

        layout.addWidget(fft_btn)
        layout.addWidget(low_btn)
        layout.addWidget(high_btn)
        layout.addWidget(band_pass_btn)
        layout.addWidget(band_stop_btn)
        layout.addWidget(inverse_btn)
        # -----------------------------
        # Radius Slider
        # -----------------------------

        row = QHBoxLayout()

        self.frequency_radius_label = QLabel(
            "Radius: 30"
        )

        self.frequency_radius_slider = QSlider(
            Qt.Orientation.Horizontal
        )

        self.frequency_radius_slider.setRange(
            5,
            150
        )

        self.frequency_radius_slider.setValue(
            30
        )

        self.frequency_radius_slider.valueChanged.connect(
            self._on_frequency_radius_changed
        )

        row.addWidget(
            self.frequency_radius_label
        )

        row.addWidget(
            self.frequency_radius_slider
        )

        layout.addLayout(row)

        return group

    ################################
    ### registration ###############
    ################################
    def _build_registration_group(self):

        group = QGroupBox("Image Registration")

        layout = QVBoxLayout(group)

        load_ref_btn = QPushButton(
            "Load Reference Image"
        )
        load_ref_btn.clicked.connect(
            self.load_reference_image
        )
        layout.addWidget(load_ref_btn)

        load_mov_btn = QPushButton(
            "Load Moving Image"
        )
        load_mov_btn.clicked.connect(
            self.load_moving_image
        )
        layout.addWidget(load_mov_btn)

        ecc_btn = QPushButton(
            "ECC Registration"
        )
        ecc_btn.clicked.connect(
            self.apply_ecc_registration
        )
        layout.addWidget(ecc_btn)

        affine_btn = QPushButton(
            "Affine Registration"
        )
        affine_btn.clicked.connect(
            self.apply_affine_registration
        )
        layout.addWidget(affine_btn)

        perspective_btn = QPushButton(
            "Perspective Registration"
        )
        perspective_btn.clicked.connect(
            self.apply_perspective_registration
        )
        layout.addWidget(perspective_btn)

        matches_btn = QPushButton(
            "Show ORB Matches"
        )
        matches_btn.clicked.connect(
            self.show_orb_matches
        )
        layout.addWidget(matches_btn)

        diff_btn = QPushButton(
            "Registration Difference"
        )
        diff_btn.clicked.connect(
            self.show_registration_difference
        )
        layout.addWidget(diff_btn)

        return group



