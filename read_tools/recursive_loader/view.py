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


class NoMarginDelegate(QtWidgets.QStyledItemDelegate):
    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ):
        option.rect.adjust(0, 0, 0, 0)  # Remove any margin
        super().paint(painter, option, index)


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

        # Create table widget
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Tree", "Name", "Type", "Range", "Path"])

        # Configure table properties
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)

        # Set custom delegate to remove margins
        delegate = NoMarginDelegate(self.table)
        self.table.setItemDelegate(delegate)

        # Set spacing and margins
        self.table.setContentsMargins(0, 0, 0, 0)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: transparent;
                spacing: 0px;
            }
            QTableWidget::item {
                padding: 0px;
                margin: 0px;
                border: none;
            }
        """)

        # Adjust row height
        self.table.verticalHeader().setDefaultSectionSize(20)  # Compact rows

        # Set font
        font = QtGui.QFont("Courier")
        font.setStyleHint(QtGui.QFont.Monospace)
        self.table.setFont(font)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Interactive)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Interactive)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Interactive)

        # Set initial column widths
        self.table.setColumnWidth(0, 400)  # Name column gets more space initially
        self.table.setColumnWidth(1, 100)  # Type column
        self.table.setColumnWidth(2, 100)  # Range column
        self.table.setColumnWidth(3, 100)  # Path column
        self.table.setColumnWidth(4, 500)  # Path column
        
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
        main_layout.addWidget(self.table)
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

        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item.flags() & QtCore.Qt.ItemIsSelectable:  # Skip directory items
                if self.table.isItemSelected(item):
                    selected_indices.append(sequence_index)
                sequence_index += 1

        return selected_indices

    def clear_list(self):
        """Clear the table"""
        self.table.setRowCount(0)

    def add_row(
        self,
        tree: str,
        name: str,
        type: str,
        range: str,
        path: str,
        selectable: bool = True,
    ):
        """Add a row to the table"""
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Replace regular spaces with figure spaces for exact width control
        name = name.replace(" ", "\u2007")

        items = [
            QtWidgets.QTableWidgetItem(tree),
            QtWidgets.QTableWidgetItem(name),
            QtWidgets.QTableWidgetItem(type),
            QtWidgets.QTableWidgetItem(range),
            QtWidgets.QTableWidgetItem(path),
        ]

        for col, item in enumerate(items):
            if not selectable:
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
            self.table.setItem(row, col, item)

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
        self.table.selectAll()
