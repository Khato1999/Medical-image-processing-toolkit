"""
The main window ties the UI (widgets.py) to the pure processing
functions (processing/*.py). It holds the only application state:
- original_image : untouched image, exactly as loaded from disk
- base_image      : current *committed* state of the processed image
                    (every non-slider action reads/writes this)
- processed_image : what's actually displayed â€” equals base_image,
                    except while brightness/contrast/gamma or Canny
                    threshold sliders are being dragged, in which case
                    it's a live preview computed from base_image that
                    hasn't been committed yet

This module only holds window/layout scaffolding â€” the panel builders
live in ui_groups.py (UIGroupsMixin) and every button/slider handler
lives in actions.py (ActionsMixin). MedicalImageToolkit is assembled
from both mixins below.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QFrame, QSplitter, QScrollArea, QTabWidget, QProgressBar
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, QSize

from .widgets import ImagePanel, ThemeToggle
from .ui_groups import UIGroupsMixin
from .actions import ActionsMixin


class MedicalImageToolkit(QMainWindow, ActionsMixin, UIGroupsMixin):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medical Image Processing Toolkit")
        self.setWindowIcon(QIcon("icons/logo.png"))
        self.resize(900, 600)

        self.original_image = None
        self.base_image = None
        self.processed_image = None
        self.dark_mode = False
        self.current_frequency_mode = None
        self.registration_reference = None
        self.registration_moving = None
        self.dicom_dataset = None
        self.current_fft = None
        self.fft_mode = False
        self.undo_stack = []
        self.redo_stack = []
        self._build_menu()
        self._build_toolbar()
        self._build_ui()



    # ---------- UI construction ----------

    def _build_menu(self):

        menubar = self.menuBar()

        # File
        file_menu = menubar.addMenu("File")

        open_action = QAction("Open Image", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)

        save_action = QAction("Save As...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_image)
        file_menu.addAction(save_action)

        # Help
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)

        help_menu.addAction(about_action)


    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        self.setMinimumSize(1400, 900)

        main_layout = QVBoxLayout(central)

        # -------------------------
        # Main horizontal splitter
        # -------------------------

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setSizes([350,1250])
        # =========================
        # LEFT SIDE: CONTROLS
        # =========================

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.West)

        # Processing
        proc_page = QWidget()
        proc_layout = QVBoxLayout(proc_page)
        proc_layout.addWidget(self._build_processing_group())
        proc_layout.addStretch()

        # Enhancement
        enh_page = QWidget()
        enh_layout = QVBoxLayout(enh_page)
        enh_layout.addWidget(self._build_enhancement_group())
        enh_layout.addStretch()

        # Filters
        filt_page = QWidget()
        filt_layout = QVBoxLayout(filt_page)
        filt_layout.addWidget(self._build_filters_group())
        filt_layout.addStretch()

        # Pipeline
        pipeline_page = QWidget()
        pipeline_layout = QVBoxLayout(pipeline_page)
        pipeline_layout.addWidget(self._build_pipeline_group())
        pipeline_layout.addStretch()

        # Edge Detection
        edge_page = QWidget()
        edge_layout = QVBoxLayout(edge_page)
        edge_layout.addWidget(self._build_edge_detection_group())
        edge_layout.addStretch()

        # Analysis
        analysis_page = QWidget()
        analysis_layout = QVBoxLayout(analysis_page)
        analysis_layout.addWidget(self._build_analysis_group())
        analysis_layout.addStretch()

        # Morphology
        morphology_page = QWidget()
        morphology_layout = QVBoxLayout(morphology_page)
        morphology_layout.addWidget(self._build_morphology_group())
        morphology_layout.addStretch()

        dicom_page = QWidget()
        dicom_layout = QVBoxLayout(dicom_page)
        dicom_layout.addWidget(self._build_dicom_group())
        dicom_layout.addStretch()

        # frequency
        frequency_page = QWidget()
        frequency_layout = QVBoxLayout(frequency_page)
        frequency_layout.addWidget(self._build_frequency_group())
        frequency_layout.addStretch()

                # Registration
        registration_page = QWidget()
        registration_layout = QVBoxLayout(registration_page)

        registration_layout.addWidget(self._build_registration_group())
        registration_layout.addStretch()


        tabs.addTab(proc_page, "Processing")
        tabs.addTab(enh_page, "Enhancement")
        tabs.addTab(filt_page, "Filters")
        tabs.addTab(frequency_page, "FFT")
        tabs.addTab(pipeline_page, "Pipeline")
        tabs.addTab(edge_page, "Edges")
        tabs.addTab(morphology_page, "Morphology")
        tabs.addTab(analysis_page, "Analysis")
        tabs.addTab(registration_page, "Registration")
        tabs.addTab(dicom_page, "DICOM")
        
        

        control_scroll = QScrollArea()
        control_scroll.setWidgetResizable(True)
        control_scroll.setWidget(tabs)
        control_scroll.setMinimumWidth(420)
        control_scroll.setMaximumWidth(500)

        splitter.addWidget(control_scroll)


        # =========================
        # RIGHT SIDE: IMAGES
        # =========================

        image_container = QWidget()
        image_layout = QVBoxLayout(image_container)

        images_layout = QHBoxLayout()
        images_layout.setSpacing(5)
        images_layout.setContentsMargins(0,0,0,0)
        self.original_panel = ImagePanel("Original Image")

        self.processed_panel = ImagePanel(
            "Processed Image",
            on_crop_selected=self._on_crop_selected
        )

        images_layout.addWidget(
            self.original_panel,
            stretch=1
        )

        images_layout.addWidget(
            self.processed_panel,
            stretch=1
        )

        image_layout.addLayout(images_layout)

        # -------------------------
        # Image information
        # -------------------------

        info_frame = QFrame()

        info_frame.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        info_layout = QHBoxLayout(info_frame)

        self.info_labels = {}

        for field in (
            "Width",
            "Height",
            "Resolution",
            "Channels",
            "Image Type",
        ):
            lbl = QLabel(f"{field}: -")
            self.info_labels[field] = lbl
            info_layout.addWidget(lbl)

        info_layout.addStretch()

        image_layout.addWidget(info_frame)

        splitter.addWidget(image_container)

        # Images should receive most space

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 5)

        main_layout.addWidget(splitter)

        # =========================
        # Bottom action buttons
        # =========================

        button_layout = QHBoxLayout()

        open_btn = QPushButton("Open Image")
        open_btn.clicked.connect(self.open_image)

        self.statusBar().showMessage(
            "Ready â€” open an image to begin"
        )

        self.status_label = QLabel("Ready")
        self.statusBar().addPermanentWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(150)
        self.progress_bar.setValue(0)
        self.statusBar().addPermanentWidget(self.progress_bar)

    def _build_toolbar(self):

        toolbar = self.addToolBar("Main")

        toolbar.setIconSize(QSize(28, 28))

        open_action = QAction(QIcon("icons/folder.svg"),"Open",self,)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_image)

        save_action = QAction(QIcon("icons/save.svg"),"Save",self,)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_image)

        reset_action = QAction(QIcon("icons/reset.svg"),"Reset", self,)
        reset_action.setShortcut("Ctrl+R")
        reset_action.triggered.connect(self.reset_image)

        self.undo_action = QAction(QIcon("icons/rotate-cw.svg"), "Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self.undo)
        self.undo_action.setEnabled(False)

        self.redo_action = QAction(QIcon("icons/rotate-ccw.svg"), "Redo", self)
        self.redo_action.setShortcut("Ctrl+Shift+Z")
        self.redo_action.triggered.connect(self.redo)
        self.redo_action.setEnabled(False)

        self.theme_switch = ThemeToggle(self.dark_mode, self)
        self.theme_switch.toggled.connect(lambda _checked: self.toggle_theme())

        toolbar.addAction(open_action)
        toolbar.addAction(save_action)
        toolbar.addAction(reset_action)
        toolbar.addSeparator()
        toolbar.addAction(self.undo_action)
        toolbar.addAction(self.redo_action)
        toolbar.addSeparator()
        toolbar.addWidget(self.theme_switch)









