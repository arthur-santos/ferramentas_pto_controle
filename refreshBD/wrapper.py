from qgis.PyQt.QtWidgets import (
    QLineEdit
)

from processing.gui.wrappers import WidgetWrapper


class MyWidgetWrapper(WidgetWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def createWidget(self):
        self._lineedit = QLineEdit()
        self._lineedit.setEchoMode(QLineEdit.Password)
        # self._lineedit.setPlaceholderText('Teste')
        widget = self._lineedit
        return widget