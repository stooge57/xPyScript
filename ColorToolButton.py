# This file is under MIT license. The license file can be obtained in the root directory of this module.

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QBrush, QColorConstants, QPainter, QPen
from PyQt6.QtWidgets import QToolButton

class ColorToolButton(QToolButton):
   @property
   def color(self):
      return(self._color)

   @color.setter
   def color(self, value):
      self._color = value
      str = f"rgb({self._color.red()}, {self._color.green()}, {self._color.blue()})"
      self.setToolTip(str)
      self.update()

   def __init__(self, parent=None):
      super().__init__(parent)
      self._color = QColorConstants.White

   def paintEvent(self, event):
      super().paintEvent(event)
      painter = QPainter(self)
      painter.setPen(QPen(QColorConstants.Black))
      painter.setBrush(QBrush(self._color))
      painter.drawRect(self.rect().adjusted(5, 5, -5, -5))