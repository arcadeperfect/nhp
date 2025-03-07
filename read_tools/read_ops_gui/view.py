from PySide2 import QtWidgets, QtCore, QtGui # type: ignore
from PySide2.QtCore import Signal # type: ignore


class View(QtWidgets.QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setWindowTitle("Read Ops")
        
        # self.setMinimumSize(800, 800)# Create main layout

        # main_layout = QtWidgets.QVBoxLayout(self)
        # self.setLayout(main_layout)
        
        # form_layout = QtWidgets.QFormLayout()
        
        # self.prefix_field = QtWidgets.QLineEdit()
        # self.delimiter_field = QtWidgets.QLineEdit()
        # self.suffix_field = QtWidgets.QLineEdit()
        # self.extension_field = QtWidgets.QLineEdit()
        
        # if padding:
        #     self.padding_field = QtWidgets.QLineEdit()
        #     validator = QtGui.QIntValidator()
        #     validator.setBottom(0)  # Only allow positive integers
        #     self.padding_field.setValidator(validator)
        
        
        # form_layout.addRow("Prefix:", self.prefix_field)
        # form_layout.addRow("Delimiter:", self.delimiter_field)
        # form_layout.addRow("Suffix:", self.suffix_field)
        # if padding:
        #     form_layout.addRow("Padding:", self.padding_field)
        # form_layout.addRow("Extension:", self.extension_field)
        
        # main_layout.addLayout(form_layout)
        
        # self.setLayout(main_layout)
        
    def initialize_fields(self, sequence):
        self.setWindowTitle("Read Ops")
        
        self.setMinimumSize(800, 800)# Create main layout

        main_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(main_layout)
        
        form_layout = QtWidgets.QFormLayout()
        
        self.prefix_field = QtWidgets.QLineEdit()

        self.extension_field = QtWidgets.QLineEdit()
        
        if sequence:
            self.delimiter_field = QtWidgets.QLineEdit()
            self.suffix_field = QtWidgets.QLineEdit()
            
            self.padding_field = QtWidgets.QLineEdit()
            validator = QtGui.QIntValidator()
            validator.setBottom(0)  # Only allow positive integers
            self.padding_field.setValidator(validator)
        
        
        form_layout.addRow("Prefix:", self.prefix_field)

        if sequence:
            form_layout.addRow("Delimiter:", self.delimiter_field)
            form_layout.addRow("Suffix:", self.suffix_field)
            form_layout.addRow("Padding:", self.padding_field)

        form_layout.addRow("Extension:", self.extension_field)
        
        main_layout.addLayout(form_layout)
        
        self.setLayout(main_layout) 
    def set_fields(self, prefix: str, delimiter: str, suffix: str, padding: int, extension: str):
        self.prefix_field.setText(prefix)
        self.delimiter_field.setText(delimiter)
        self.suffix_field.setText(suffix)
        self.padding_field.setText(str(padding))
        self.extension_field.setText(extension)
        
        
