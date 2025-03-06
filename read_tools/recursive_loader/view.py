from PySide2 import QtWidgets
from PySide2.QtCore import Signal, Qt, QSize
from pathlib import Path
from typing import List

from nhp.read_tools.recursive_loader import widgets


class View(QtWidgets.QWidget):
    # Signals
    directory_selected = Signal(Path)  # Emitted when directory is chosen
    load_requested = Signal(list)  # Emitted with list of selected indices
    cancel_requested = Signal()  # Emitted when cancel is clicked
    scan_requested = Signal()  # Emitted when scan is clicked
    select_all_requested = Signal()  # Emitted when select all is clicked
    deselect_all_requested = Signal()  # Emitted when deselect all is clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sequence Loader")
        
        # Create main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # Create path selection layout
        path_layout = QtWidgets.QHBoxLayout()
        self.line_edit_path = QtWidgets.QLineEdit()
        self.button_browse = QtWidgets.QPushButton("Browse")
        self.button_scan = QtWidgets.QPushButton("Scan")
        
        path_layout.addWidget(self.line_edit_path)
        path_layout.addWidget(self.button_browse)
        path_layout.addWidget(self.button_scan)
        
        # Create list widget
        self.list_sequences = QtWidgets.QListWidget()
        self.list_sequences.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        
        # Create button layout
        button_layout = QtWidgets.QHBoxLayout()
        self.button_select_all = QtWidgets.QPushButton("Select All")
        self.button_deselect_all = QtWidgets.QPushButton("Deselect All")
        self.button_load = QtWidgets.QPushButton("Load")
        self.button_cancel = QtWidgets.QPushButton("Cancel")
        
        
        button_layout.addWidget(self.button_select_all)
        button_layout.addWidget(self.button_deselect_all)
        button_layout.addStretch()  # This pushes Load and Cancel to the right
        button_layout.addWidget(self.button_load)
        button_layout.addWidget(self.button_cancel)
        
        # Add all layouts to main layout
        main_layout.addLayout(path_layout)
        main_layout.addWidget(self.list_sequences)
        main_layout.addLayout(button_layout)
        
        # Connect signals
        self.button_browse.clicked.connect(self._on_browse_clicked)
        self.button_scan.clicked.connect(self._on_scan_clicked)
        self.button_select_all.clicked.connect(self._on_select_all_clicked)
        self.button_deselect_all.clicked.connect(self._on_deselect_all_clicked)
        self.button_load.clicked.connect(self._on_load_clicked)
        self.button_cancel.clicked.connect(self._on_cancel_clicked)
        
        # Set minimum size
        self.setMinimumSize(1400, 800)


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

    def _on_select_all_clicked(self):
        """Handle select all button click"""
        self.select_all_requested.emit()

    def _on_deselect_all_clicked(self):
        """Handle deselect all button click"""
        self.deselect_all_requested.emit()

    def get_selected_indices(self) -> List[int]:
        """Get indices of selected items that correspond to image files"""
        image_file_index = 0  # Counter for actual image files
        selected_indices = []
        
        for i in range(self.list_sequences.count()):
            item = self.list_sequences.item(i)
            widget = self.list_sequences.itemWidget(item)
            
            # Skip directory items
            if isinstance(widget, widgets.DirectoryListItem):
                continue
                
            if item.isSelected():
                selected_indices.append(image_file_index)
                
            image_file_index += 1
            
        return selected_indices

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

    def select_all(self):
        """Select all items"""
        self.list_sequences.selectAll()

    def deselect_all(self):
        """Deselect all items"""
        self.list_sequences.clearSelection()