from pathlib import Path
from typing import List, Optional
from PySide2 import QtWidgets, QtCore
from nhp.read_tools.read_wrapper import ImageFile, MovieFile, ReadWrapper
from nhp.read_tools.recursive_loader import nuke_interface
from nhp.read_tools.recursive_loader.view import View
from nhp.read_tools.recursive_loader.model import Model


class Controller:
    def __init__(self, view: View, model: Model, path: Optional[Path] = None):
        self.view = view
        self.model = model
        
        # Connect signals
        self.view.directory_selected.connect(self._on_directory_selected)
        self.view.scan_requested.connect(self._on_scan_requested)
        self.view.load_requested.connect(self._on_load_requested)
        self.view.cancel_requested.connect(self._on_cancel_requested)
        self.view.select_all_requested.connect(self._on_select_all_requested)
        
        if path:
            self._on_directory_selected(path)
            self._on_scan_requested()         

    def populate_list(self):
        """Populate the table with the directory tree"""
        self.view.clear_list()
        
        if not self.model.current_directory:
            return
            
        tree = self.model.build_directory_tree()
        if tree:
            self.view.tree_presenter.display_tree(tree)

    def _on_directory_selected(self, directory: Path):
        """Handle directory selection"""
        self.model.clear()
        self.view.clear_list()
        self.view.set_path_text(str(directory))
        self.model._current_directory = directory

    def _on_scan_requested(self):
        """Handle scan request"""
        try:
            directory = Path(self.view.get_path_text())
            self.model.scan_directory(directory)
            self.populate_list()
        except Exception as e:
            self.view.show_error(str(e))

    def _on_load_requested(self, id_list: List[int]):
        """Handle load request"""
        
        if not self.model._node:
            return
        
        try:
            nuke_interface.generate_read_nodes_2(
                [self.model.ImageFileById[id] for id in id_list]
            )
        except Exception as e:
            self.view.show_error(str(e))

    def _on_cancel_requested(self):
        """Handle cancel request"""
        self.view.close()

    def _on_select_all_requested(self):
        """Handle select all request"""
        self.view.select_all()