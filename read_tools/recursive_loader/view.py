from PySide2 import QtWidgets, QtCore, QtGui
# from PySide2 import QtWidgets
from PySide2.QtCore import Signal
from pathlib import Path
from typing import List

class SynchronizedListWidget(QtWidgets.QListWidget):
    """Custom QListWidget that syncs its scrolling with others"""
    def __init__(self, sync_lists=None, parent=None, selectable=False):
        super().__init__(parent)
        self.sync_lists = sync_lists or []
        
        # Configure selection
        if selectable:
            self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        else:
            self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        
        font = QtGui.QFont("Courier")  # or try "Menlo" or "Monaco" on Mac
        font.setStyleHint(QtGui.QFont.Monospace)
        self.setFont(font)
        
        
        # Sync scrolling
        self.verticalScrollBar().valueChanged.connect(self._sync_scroll)
        
    def add_sync_list(self, list_widget):
        """Add a list to sync with"""
        if list_widget not in self.sync_lists:
            self.sync_lists.append(list_widget)
            
    def _sync_scroll(self, value):
        """Sync scroll position with other lists"""
        for lst in self.sync_lists:
            if lst.verticalScrollBar().value() != value:
                lst.verticalScrollBar().setValue(value)

class View(QtWidgets.QWidget):
    # Signals
    directory_selected = Signal(Path)
    scan_requested = Signal()
    load_requested = Signal(list)
    cancel_requested = Signal()
    select_all_requested = Signal()
    
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
        
        # Create lists layout
        lists_layout = QtWidgets.QHBoxLayout()
        
        # Create synchronized lists
        self.list_names = SynchronizedListWidget(selectable=True)  # Only names list is selectable
        self.list_types = SynchronizedListWidget(selectable=False)
        self.list_ranges = SynchronizedListWidget(selectable=False)
        
        # Set up sync relationships
        self.list_names.add_sync_list(self.list_types)
        self.list_names.add_sync_list(self.list_ranges)
        self.list_types.add_sync_list(self.list_names)
        self.list_types.add_sync_list(self.list_ranges)
        self.list_ranges.add_sync_list(self.list_names)
        self.list_ranges.add_sync_list(self.list_types)
        
        # Set headers
        name_header = QtWidgets.QLabel("Name")
        type_header = QtWidgets.QLabel("Type")
        range_header = QtWidgets.QLabel("Range")
        
        # Create column layouts
        name_layout = QtWidgets.QVBoxLayout()
        type_layout = QtWidgets.QVBoxLayout()
        range_layout = QtWidgets.QVBoxLayout()
        
        name_layout.addWidget(name_header)
        name_layout.addWidget(self.list_names)
        type_layout.addWidget(type_header)
        type_layout.addWidget(self.list_types)
        range_layout.addWidget(range_header)
        range_layout.addWidget(self.list_ranges)
        
        # Set column widths
        self.list_names.setMinimumWidth(300)
        self.list_types.setFixedWidth(100)
        self.list_ranges.setFixedWidth(100)
        
        lists_layout.addLayout(name_layout)
        lists_layout.addLayout(type_layout)
        lists_layout.addLayout(range_layout)
        
        # Create button layout
        button_layout = QtWidgets.QHBoxLayout()
        self.button_select_all = QtWidgets.QPushButton("Select All")
        self.button_load = QtWidgets.QPushButton("Load")
        self.button_cancel = QtWidgets.QPushButton("Cancel")
        
        button_layout.addWidget(self.button_select_all)
        button_layout.addStretch()
        button_layout.addWidget(self.button_load)
        button_layout.addWidget(self.button_cancel)
        
        # Add all layouts to main layout
        main_layout.addLayout(path_layout)
        main_layout.addLayout(lists_layout)
        main_layout.addLayout(button_layout)
        
        # Connect signals
        self.button_browse.clicked.connect(self._on_browse_clicked)
        self.button_scan.clicked.connect(self._on_scan_clicked)
        self.button_select_all.clicked.connect(self._on_select_all_clicked)
        self.button_load.clicked.connect(self._on_load_clicked)
        self.button_cancel.clicked.connect(self._on_cancel_clicked)
        
        # Set minimum size
        self.setMinimumSize(1400, 800)

    def _on_browse_clicked(self):
        """Handle browse button click"""
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory", str(Path.home())
        )
        if directory:
            self.directory_selected.emit(Path(directory))

    def _on_scan_clicked(self):
        """Handle scan button click"""
        self.scan_requested.emit()

    def _on_select_all_clicked(self):
        """Handle select all button click"""
        self.select_all_requested.emit()

    def _on_load_clicked(self):
        """Handle load button click"""
        selected = self.get_selected_indices()
        if selected:
            self.load_requested.emit(selected)

    def _on_cancel_clicked(self):
        """Handle cancel button click"""
        self.cancel_requested.emit()

    def get_selected_indices(self) -> List[int]:
        """Get indices of selected items that correspond to image files"""
        selected_indices = []
        sequence_index = 0
        
        for i in range(self.list_names.count()):
            item = self.list_names.item(i)
            if item.flags() & QtCore.Qt.ItemIsSelectable:  # Skip directory items
                if item.isSelected():
                    selected_indices.append(sequence_index)
                sequence_index += 1
                
        return selected_indices

    def clear_list(self):
        """Clear all lists"""
        self.list_names.clear()
        self.list_types.clear()
        self.list_ranges.clear()

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

    def select_all(self):
        """Select all selectable items"""
        self.list_names.selectAll()