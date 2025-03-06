import nuke
from PySide2 import QtWidgets, QtCore, QtGui

# class CustomListItem(QtWidgets.QWidget):
#     """
#     Custom widget that contains three text fields: name, ext, and framerange
#     for displaying discovered image sequences
#     while maintaining selectability in a QListWidget
#     """
#     def __init__(self, parent=None):
#         super(CustomListItem, self).__init__(parent)

#         self.layout = QtWidgets.QHBoxLayout(self)
#         self.layout.setContentsMargins(4, 2, 4, 2)
#         self.layout.setSpacing(2)  
        
#         self.nameLabel = QtWidgets.QLabel("Name:")
#         self.nameField = QtWidgets.QLineEdit()
#         self.nameField.setReadOnly(True)
        
#         self.typeLabel = QtWidgets.QLabel("Type:")
#         self.typeField = QtWidgets.QLineEdit()
#         self.typeField.setReadOnly(True)
        
#         self.rangeLabel = QtWidgets.QLabel("Range:")
#         self.rangeField = QtWidgets.QLineEdit()
#         self.rangeField.setReadOnly(True)
        
#         self.layout.addWidget(self.nameLabel)
#         self.layout.addWidget(self.nameField, 3)
#         self.layout.addWidget(self.typeLabel)
#         self.layout.addWidget(self.typeField, 1)
#         self.layout.addWidget(self.rangeLabel)
#         self.layout.addWidget(self.rangeField, 1)
        
#     def set_data(self, name: str, type: str, range: str):
#         self.nameField.setText(name)
#         self.typeField.setText(type)
#         self.rangeField.setText(range)
        
# class DirectoryListItem(QtWidgets.QWidget):
#     """
#     Widget that displays a directory path
#     for grouping sequences in a QListWidget
#     """
#     def __init__(self, parent=None):
#         super(DirectoryListItem, self).__init__(parent)

#         # Create layout
#         self.layout = QtWidgets.QHBoxLayout(self)
#         self.layout.setContentsMargins(4, 2, 4, 2)
#         self.layout.setSpacing(2)
        
#         # Create path label
#         self.pathLabel = QtWidgets.QLabel()
#         self.pathLabel.setStyleSheet("""
#             QLabel {
#                 background-color: #444444;
#                 color: #ffffff;
#                 padding: 2px;
#             }
#         """)
        
#         # Add widget to layout
#         self.layout.addWidget(self.pathLabel)
        
#     def set_data(self, path: str):
#         """Set the directory path"""
#         self.pathLabel.setText(path)


class DirectoryListItem(QtWidgets.QWidget):
    """Widget that displays a directory path with indentation"""
    def __init__(self, parent=None):
        super(DirectoryListItem, self).__init__(parent)
        
        # Create layout
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(4, 2, 4, 2)
        self.layout.setSpacing(2)
        
        # Create spacer widget for indentation
        self.indent_widget = QtWidgets.QWidget()
        self.layout.addWidget(self.indent_widget)
        
        # Create path label
        self.pathLabel = QtWidgets.QLabel()
        self.pathLabel.setStyleSheet("""
            QLabel {
                background-color: #444444;
                color: #ffffff;
                padding: 2px;
            }
        """)
        
        # Add widget to layout
        self.layout.addWidget(self.pathLabel, 1)
        
    def set_data(self, path: str, depth: int):
        """Set the directory path and indentation"""
        self.pathLabel.setText(path)
        self.indent_widget.setFixedWidth(depth * 25)  # 25 pixels per indent level

class CustomListItem(QtWidgets.QWidget):
    """Custom widget for displaying sequence information with indentation"""
    def __init__(self, parent=None):
        super(CustomListItem, self).__init__(parent)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(4, 2, 4, 2)
        self.layout.setSpacing(2)
        
        # Create spacer widget for indentation
        self.indent_widget = QtWidgets.QWidget()
        self.layout.addWidget(self.indent_widget)
        
        # Create fields
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
        
    def set_data(self, name: str, type: str, range: str, depth: int):
        """Set the data and indentation"""
        self.nameField.setText(name)
        self.typeField.setText(type)
        self.rangeField.setText(range)
        self.indent_widget.setFixedWidth(depth * 25)  # 25 pixels per indent level