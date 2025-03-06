import nuke
from PySide2 import QtWidgets, QtCore, QtGui

class CustomListItem(QtWidgets.QWidget):
    """
    Custom widget that contains three text fields: name, ext, and framerange
    for displaying discovered image sequences
    while maintaining selectability in a QListWidget
    """
    def __init__(self, parent=None):
        super(CustomListItem, self).__init__(parent)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(4, 2, 4, 2)
        self.layout.setSpacing(2)  
        
        self.nameLabel = QtWidgets.QLabel("Name:")
        self.nameField = QtWidgets.QLineEdit()
        self.nameField.setReadOnly(True)
        
        self.typeLabel = QtWidgets.QLabel("Type:")
        self.typeField = QtWidgets.QLineEdit()
        self.typeField.setReadOnly(True)
        
        self.rangeLabel = QtWidgets.QLabel("Range:")
        self.rangeField = QtWidgets.QLineEdit()
        self.rangeField.setReadOnly(True)
        
        self.layout.addWidget(self.nameLabel)
        self.layout.addWidget(self.nameField, 3)
        self.layout.addWidget(self.typeLabel)
        self.layout.addWidget(self.typeField, 1)
        self.layout.addWidget(self.rangeLabel)
        self.layout.addWidget(self.rangeField, 1)
        
    def set_data(self, name: str, type: str, range: str):
        self.nameField.setText(name)
        self.typeField.setText(type)
        self.rangeField.setText(range)
        
        
        