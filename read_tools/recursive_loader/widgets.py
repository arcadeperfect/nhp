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
        
        self.layout.addWidget(self.nameLabel)
        self.layout.addWidget(self.nameField, 3)
        
    def set_data(self, name=""):
        self.nameField.setText(name)
        
        
        