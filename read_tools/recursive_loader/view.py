from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Signal
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from nhp.read_tools.read_wrapper import ImageFile
from .model import DirectoryTree
import nuke

class TreePresenter:
    
    def __init__(self, view: 'View'):
        self.view = view

    def display_tree(self, tree: DirectoryTree) -> None:
        """Display the directory tree in the view"""
        self._display_node(tree)

    def _display_node(self, node: DirectoryTree, prefix: str = "", is_last: bool = True) -> None:
        """Recursively display a node and its children"""
        # Skip displaying root directory
        if node.name:
            self.view.add_row(
                self._format_directory(prefix, is_last, node.name),
                "",  # name
                "",  # type
                "",  # range
                "",  # path
                -1,
                selectable=False
            )
        
        # Create new prefix for children
        new_prefix = prefix
        if node.name:  # Not for root
            new_prefix = prefix + ("    " if is_last else "│   ")
        
        # Process subdirectories first
        for i, subdir in enumerate(sorted(node.subdirs, key=lambda x: x.name)):
            is_last_dir = i == len(node.subdirs) - 1
            is_last_item = is_last_dir and not node.files
            self._display_node(subdir, new_prefix, is_last_item)
        
        # Then process files
        for i, file in enumerate(node.files):
            is_last_file = i == len(node.files) - 1
            file_prefix = new_prefix + ("└── " if is_last_file else "├── ")
            
            if file.id is None:
                raise ValueError(f"File {file.name} has no id")
            
            self.view.add_row(
                f"{file_prefix}[{file.extension.upper()}]",
                file.name,
                file.extension.upper(),
                self._get_frame_range(file),
                str(file.get_path()),
                file.id
            )

    @staticmethod
    def _format_directory(prefix: str, is_last: bool, name: str) -> str:
        """Format a directory name with the appropriate prefix"""
        return f"{prefix}{'└── ' if is_last else '├── '}{name}/"

    @staticmethod
    def _get_frame_range(file: ImageFile) -> str:
        """Get frame range string for an image file"""
        if file.frame_count > 1:
            return f"{file.first_frame()}-{file.last_frame()}"
        elif file.frame_count == -1:
            return "Unknown"
        else:
            return "Single Frame"


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
        self.tree_presenter = TreePresenter(self)

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
        self.table.setColumnWidth(0, 400)  # Tree
        self.table.setColumnWidth(1, 200)  # Name
        self.table.setColumnWidth(2, 50)  # Type
        self.table.setColumnWidth(3, 100)  # Range
        self.table.setColumnWidth(4, 500)  # Path
        
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
        
        self.__row_counter = 0
        self.id_lookup: dict[int, int] = {}

    def _on_browse_clicked(self):
        """Handle browse button click"""
        directory = Path(nuke.getFilename("Select Directory"))
        
        if directory.is_dir():
            if not directory.exists():
                return
        else:
            directory = directory.parent
            if not directory.exists():
                return
        
        if directory:
            self.directory_selected.emit(directory)
        # directory = QtWidgets.QFileDialog.getExistingDirectory(
        #     self, "Select Directory", str(Path.home())
        # )
        # if directory:
        #     self.directory_selected.emit(Path(directory))

    def _on_scan_clicked(self):
        """Handle scan button click"""
        self.scan_requested.emit()

    def _on_select_all_clicked(self):
        """Handle select all button click"""
        self.select_all_requested.emit()

    def _on_load_clicked(self):
        """Handle load button click"""
        # selected = self.get_selected_indices()
        # if selected:
        #     self.load_requested.emit(selected)
        self.load_requested.emit(self.get_selected_ids())

    def _on_cancel_clicked(self):
        """Handle cancel button click"""
        self.cancel_requested.emit()

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
        id: int,
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
        
        
        if id != -1:
            self.id_lookup[self.__row_counter] = id
        self.__row_counter += 1

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

    def get_selected_indeces(self) -> List[int]:
            """Get indices of selected rows"""
            selected_ranges = self.table.selectedRanges()
            selected_rows = set()
            for range_ in selected_ranges:
                for row in range(range_.topRow(), range_.bottomRow() + 1):
                    # Check if the item in the first column is selectable
                    item = self.table.item(row, 0)
                    if item and item.flags() & QtCore.Qt.ItemIsSelectable:
                        selected_rows.add(row)
            return list(selected_rows)

    def get_selected_ids(self) -> List[int]:
        
        # print("--------------------------------")
        # print("key values")
        # # print(self.id_lookup)
        # for key, value in self.id_lookup.items():
        #     print(f"key: {key}, value: {value}")
        
        # print("---------------")
        # print("selected indeces")
        # print(self.get_selected_indeces())
        
        # for s in self.get_selected_indeces():
        #     print(self.id_lookup[s])
            
            
        return [self.id_lookup[s] for s in self.get_selected_indeces()]