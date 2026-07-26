"""
Medical Image Processing Toolkit — entry point.

Run with:  python main.py
Requires:  pip install -r requirements.txt

See toolkit/main_window.py for the application window and
toolkit/processing/ for the actual image-processing functions.
"""

import sys

from PyQt6.QtWidgets import QApplication
from toolkit.main_window import MedicalImageToolkit
from toolkit.theme import LIGHT_THEME


def main():
    app = QApplication(sys.argv)

    app.setApplicationName(
        "Medical Image Processing Toolkit"
    )

    app.setOrganizationName(
        "Khato"
    )

    app.setStyleSheet(LIGHT_THEME)

    window = MedicalImageToolkit()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
