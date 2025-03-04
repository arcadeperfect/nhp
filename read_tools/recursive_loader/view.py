from PySide2 import QtWidgets
from PySide2 import QtCore


class View(QtWidgets.QWidget):
    
    def __init__(self):
        super().__init__()
        print("init view")
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Recursive Loader")
        self.setMinimumSize(QtCore.QSize(1400, 600))
        
        # Create widgets
        self.create_widgets()
        
        # Create layouts
        self.create_layouts()
        
        # Setup layouts
        self.setup_layouts()
        
    def create_widgets(self):
        # Browse button
        self.button_browse = QtWidgets.QPushButton("Browse...")
        self.button_browse.setMaximumWidth(100)
        
        # Path display
        self.line_edit_path = QtWidgets.QLineEdit()
        self.line_edit_path.setReadOnly(True)
        
        # List widget for showing found sequences
        self.list_sequences = QtWidgets.QListWidget()
        
        # Bottom buttons
        self.button_load = QtWidgets.QPushButton("Load Selected")
        self.button_cancel = QtWidgets.QPushButton("Cancel")
        
    def create_layouts(self):
        # Main layout
        self.layout_main = QtWidgets.QVBoxLayout()
        
        # Path selection layout
        self.layout_path = QtWidgets.QHBoxLayout()
        
        # Buttons layout
        self.layout_buttons = QtWidgets.QHBoxLayout()
        
    def setup_layouts(self):
        # Setup path selection layout
        self.layout_path.addWidget(self.line_edit_path)
        self.layout_path.addWidget(self.button_browse)
        
        # Setup buttons layout
        self.layout_buttons.addStretch()
        self.layout_buttons.addWidget(self.button_load)
        self.layout_buttons.addWidget(self.button_cancel)
        
        # Setup main layout
        self.layout_main.addLayout(self.layout_path)
        self.layout_main.addWidget(self.list_sequences)
        self.layout_main.addLayout(self.layout_buttons)
        
        # Set the main layout
        self.setLayout(self.layout_main)