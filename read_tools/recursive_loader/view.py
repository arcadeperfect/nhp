from PySide2 import QtWidgets
from PySide2.QtCore import Signal, Qt, QSize
from pathlib import Path
from typing import List


class View(QtWidgets.QWidget):
    # Signals
    directory_selected = Signal(Path)  # Emitted when directory is chosen
    load_requested = Signal(list)  # Emitted with list of selected indices
    cancel_requested = Signal()  # Emitted when cancel is clicked
    scan_requested = Signal()  # Emitted when scan is clicked

    def __init__(self):
        super().__init__()
        print("init view")
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Recursive Loader")
        self.setMinimumSize(QSize(1400, 600))

        # Create widgets
        self.create_widgets()

        # Create layouts
        self.create_layouts()

        # Setup layouts
        self.setup_layouts()

        # Connect signals
        self.connect_signals()

        # Set window flags
        self.setWindowFlags(Qt.Window)

    def create_widgets(self):
        # Browse button
        self.button_browse = QtWidgets.QPushButton("Browse...")
        self.button_browse.setMaximumWidth(100)

        # Path display
        self.line_edit_path = QtWidgets.QLineEdit()
        self.line_edit_path.setPlaceholderText("Path to search")

        # List widget for showing found sequences
        self.list_sequences = QtWidgets.QListWidget()
        # self.list_sequences.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.list_sequences.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        # Bottom buttons
        self.button_load = QtWidgets.QPushButton("Load Selected")
        self.button_cancel = QtWidgets.QPushButton("Cancel")
        self.button_scan = QtWidgets.QPushButton("Scan")

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
        self.layout_buttons.addWidget(self.button_scan)
        self.layout_buttons.addStretch()
        self.layout_buttons.addWidget(self.button_load)
        self.layout_buttons.addWidget(self.button_cancel)

        # Setup main layout
        self.layout_main.addLayout(self.layout_path)
        self.layout_main.addWidget(self.list_sequences)
        self.layout_main.addLayout(self.layout_buttons)

        # Set the main layout
        self.setLayout(self.layout_main)

    def connect_signals(self):
        """Connect internal signals"""
        self.button_browse.clicked.connect(self._on_browse_clicked)
        self.button_load.clicked.connect(self._on_load_clicked)
        self.button_cancel.clicked.connect(self._on_cancel_clicked)
        self.button_scan.clicked.connect(self._on_scan_clicked)

    def _on_scan_clicked(self):
        """Handle scan button click"""
        print("scan button clicked")
        self.scan_requested.emit()

    def _on_browse_clicked(self):
        """Handle browse button click"""
        print("browse button clicked")
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory", str(Path.home())
        )
        if directory:
            print(f"emittiing directory: {directory}")
            self.directory_selected.emit(Path(directory))
        else:
            print("no directory selected")

    def _on_load_clicked(self):
        """Handle load button click"""
        selected = self.get_selected_indices()
        if selected:
            self.load_requested.emit(selected)

    def _on_cancel_clicked(self):
        """Handle cancel button click"""
        self.cancel_requested.emit()

    def get_selected_indices(self) -> List[int]:
        """Get indices of selected items"""
        # selected = []
        # for i in range(self.list_sequences.count()):
        #     item = self.list_sequences.item(i)
        #     widget = self.list_sequences.itemWidget(item)
        #     if widget.is_selected:
        #         selected.append(i)
        # return selected

        return [
            i
            for i in range(self.list_sequences.count())
            if self.list_sequences.item(i).isSelected()
        ]

    def clear_list(self):
        """Clear all items from list"""
        self.list_sequences.clear()

    def set_path_text(self, path: str):
        """Set the path display text"""
        print(f"setting path text: {path}")
        self.line_edit_path.setText(path)

    def get_path_text(self) -> str:
        """Get the path text"""
        return self.line_edit_path.text()

    def show_error(self, message: str):
        """Show error message to user"""
        QtWidgets.QMessageBox.critical(self, "Error", message)

    def show_info(self, message: str):
        """Show info message to user"""
        QtWidgets.QMessageBox.information(self, "Info", message)

    def add_sequence_widget(self, widget) -> None:
        """Add a sequence widget to the list"""
        # item = QtWidgets.QListWidgetItem(self.list_sequences)
        # item.setSizeHint(QSize(0, 80))
        # self.list_sequences.setItemWidget(item, widget)
