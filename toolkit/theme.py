"""
theme.py

Professional medical imaging themes.

Author: Khato
"""


# ==========================================================
# DARK THEME
# ==========================================================

DARK_THEME = """
QMainWindow {
    background-color: #202124;
}

QWidget {
    background-color: #202124;
    color: #E8EAED;
    font-size: 10pt;
}

/* -------------------------------------------------- */
/* MENU BAR */
/* -------------------------------------------------- */

QMenuBar {
    background-color: #2D2F31;
    color: #E8EAED;
}

QMenuBar::item:selected {
    background-color: #0078D4;
}

QMenu {
    background-color: #2D2F31;
    color: #E8EAED;
}

QMenu::item:selected {
    background-color: #0078D4;
}

/* -------------------------------------------------- */
/* TOOLBAR */
/* -------------------------------------------------- */

QToolBar {
    background-color: #2D2F31;
    spacing: 6px;
    border: none;
}

/* -------------------------------------------------- */
/* BUTTONS */
/* -------------------------------------------------- */

QPushButton {
    background-color: #2D2F31;
    color: white;
    border: 1px solid #555;
    border-radius: 6px;
    padding: 6px;
}

QPushButton:hover {
    background-color: #3A3D40;
}

QPushButton:pressed {
    background-color: #1B1D1F;
}

/* -------------------------------------------------- */
/* GROUPBOX */
/* -------------------------------------------------- */

QGroupBox {
    border: 1px solid #555;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0px 5px;
}

/* -------------------------------------------------- */
/* TABS */
/* -------------------------------------------------- */

QTabWidget::pane {
    border: 1px solid #555;
}

QTabBar::tab {
    background: #2D2F31;
    color: #E8EAED;
    padding: 8px;
    min-width: 120px;
}

QTabBar::tab:selected {
    background: #0078D4;
    color: white;
}

QTabBar::tab:hover {
    background: #3A3D40;
}

/* -------------------------------------------------- */
/* SLIDERS */
/* -------------------------------------------------- */

QSlider::groove:horizontal {
    border: 1px solid #444;
    height: 6px;
    background: #444;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #0078D4;
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

/* -------------------------------------------------- */
/* SCROLL AREA */
/* -------------------------------------------------- */

QScrollArea {
    border: none;
}

/* -------------------------------------------------- */
/* LABELS */
/* -------------------------------------------------- */

QLabel {
    color: #E8EAED;
}

/* -------------------------------------------------- */
/* STATUS BAR */
/* -------------------------------------------------- */

QStatusBar {
    background-color: #1B1C1D;
    color: #E8EAED;
}
"""


# ==========================================================
# LIGHT THEME
# ==========================================================

LIGHT_THEME = """
QMainWindow {
    background-color: white;
}

QWidget {
    background-color: white;
    color: black;
    font-size: 10pt;
}

/* -------------------------------------------------- */
/* MENU BAR */
/* -------------------------------------------------- */

QMenuBar {
    background-color: #F0F0F0;
    color: black;
}

QMenuBar::item:selected {
    background-color: #4A90E2;
}

QMenu {
    background-color: white;
    color: black;
}

QMenu::item:selected {
    background-color: #4A90E2;
    color: white;
}

/* -------------------------------------------------- */
/* TOOLBAR */
/* -------------------------------------------------- */

QToolBar {
    background-color: #F5F5F5;
    spacing: 6px;
    border: none;
}

/* -------------------------------------------------- */
/* BUTTONS */
/* -------------------------------------------------- */

QPushButton {
    background-color: #F0F0F0;
    color: black;
    border: 1px solid #C0C0C0;
    border-radius: 6px;
    padding: 6px;
}

QPushButton:hover {
    background-color: #E6E6E6;
}

QPushButton:pressed {
    background-color: #DADADA;
}

/* -------------------------------------------------- */
/* GROUPBOX */
/* -------------------------------------------------- */

QGroupBox {
    border: 1px solid #BFBFBF;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0px 5px;
}

/* -------------------------------------------------- */
/* TABS */
/* -------------------------------------------------- */

QTabWidget::pane {
    border: 1px solid #BFBFBF;
}

QTabBar::tab {
    background: #EFEFEF;
    color: black;
    padding: 8px;
    min-width: 120px;
}

QTabBar::tab:selected {
    background: #4A90E2;
    color: white;
}

QTabBar::tab:hover {
    background: #D9E8FA;
}

/* -------------------------------------------------- */
/* SLIDERS */
/* -------------------------------------------------- */

QSlider::groove:horizontal {
    border: 1px solid #C0C0C0;
    height: 6px;
    background: #D7D7D7;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #4A90E2;
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

/* -------------------------------------------------- */
/* SCROLL AREA */
/* -------------------------------------------------- */

QScrollArea {
    border: none;
}

/* -------------------------------------------------- */
/* LABELS */
/* -------------------------------------------------- */

QLabel {
    color: black;
}

/* -------------------------------------------------- */
/* STATUS BAR */
/* -------------------------------------------------- */

QStatusBar {
    background-color: #F0F0F0;
    color: black;
}
"""