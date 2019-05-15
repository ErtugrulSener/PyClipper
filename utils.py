from PyQt5.QtWidgets import (QFrame, QWidget)


class WidgetUtils:

    @staticmethod
    def add_widget_with_alignment(master, widget, layout, alignment=False):
        tmp_layout = layout()
        tmp_layout.addWidget(widget)
        tmp_layout.setSpacing(0)
        tmp_layout.setContentsMargins(0, 0, 0, 0)

        if alignment:
            tmp_layout.setAlignment(alignment)

        tmp_frame = QFrame(master)
        tmp_frame.resize(master.width(), 50)
        tmp_frame.setLayout(tmp_layout)

        return tmp_frame, tmp_layout

    @staticmethod
    def get_label_size(elem1):
        rect = elem1.fontMetrics().boundingRect(elem1.text())
        return rect.width(), rect.height()

    @staticmethod
    def horizontal_align_center(elem1, elem2):
        elem1_width = elem1.frameGeometry().width() if isinstance(elem1, QWidget) else int(elem1)
        elem2_width = elem2.frameGeometry().width() if isinstance(elem2, QWidget) else int(elem2)

        return (elem1_width // 2) - (elem2_width // 2)

    @staticmethod
    def vertical_align_center(elem1, elem2):
        elem1_height = elem1.frameGeometry().height() if isinstance(elem1, QWidget) else int(elem1)
        elem2_height = elem2.frameGeometry().height() if isinstance(elem2, QWidget) else int(elem2)

        return (elem1_height // 2) - (elem2_height // 2)
