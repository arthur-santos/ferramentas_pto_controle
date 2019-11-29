from qgis.PyQt.QtWidgets import (
    QLineEdit
)

from processing.gui.wrappers import WidgetWrapper


class MyWidgetWrapper(WidgetWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.placeholder = args[0]

    def createWidget(self):
        self._lineedit = QLineEdit()
        self._lineedit.setEchoMode(QLineEdit.Password)
        if self.placeholder: self._lineedit.setPlaceholderText(self.placeholder)
        widget = self._lineedit
        return widget