from pathlib import Path
from typing import List
from nhp.read_tools.read_wrapper import ImageFile, ReadWrapper
from PySide2 import QtWidgets
from PySide2 import QtCore
from nhp.read_tools.recursive_loader import widgets

# from nhp.read_tools.recursive_loader.widgets import SequenceWidget
from nhp.read_tools.recursive_loader.view import View
from nhp.read_tools.recursive_loader.model import Model
from pysequitur import crawl


class Controller:
    def __init__(self, view: View, model: Model):
        print("controller init 2")
        self.view = view
        self.model = model

        # Connect signals
        self.view.directory_selected.connect(lambda x: self.on_directory_selected(x))
        self.view.scan_requested.connect(self.on_scan_requested)
        self.view.load_requested.connect(self.on_load_requested)
        self.view.cancel_requested.connect(self.on_cancel_requested)
        self.view.select_all_requested.connect(self.on_select_all_requested)
        self.view.deselect_all_requested.connect(self.on_deselect_all_requested)

        # debug
        self.on_directory_selected(Path("/Volumes/porb/test_seqs"))
        self.on_scan_requested()

    def on_directory_selected(self, directory: Path):
        """Handle directory selection"""
        print(f"on_directory_selected: {directory}")

        self.view.set_path_text(str(directory))

    def on_scan_requested(self):
        """Handle scan request"""
        print("on_scan_requested")
        self.model.scan_directory(Path(self.view.get_path_text()))
        crawl.visualize_tree(self.model._node)
        self.populate_list()

    # def populate_list(self):
    #     """Populate the list with the sequences"""
    #     # Clear existing items
    #     self.view.clear_list()

    #     for i, image_file in enumerate(self.model._ImageFiles):
    #         list_item = QtWidgets.QListWidgetItem()
    #         custom_widget = widgets.ImageFileListItem()
    #         custom_widget.set_data(
    #             image_file.name,
    #             image_file.extension.upper(),
    #             self.get_frame_range(image_file),
    #         )
    #         list_item.setSizeHint(custom_widget.sizeHint())

    #         self.view.list_sequences.addItem(list_item)
    #         self.view.list_sequences.setItemWidget(list_item, custom_widget)
    def populate_list(self):
        """Populate the list with the sequences"""
        self.view.clear_list()
        
        current_dir = None
        for image_file in self.model._ImageFiles:
            # If we encounter a new directory, add a directory item
            if current_dir != image_file.directory:
                current_dir = image_file.directory
                list_item = QtWidgets.QListWidgetItem()
                list_item.setFlags(list_item.flags() & ~QtCore.Qt.ItemIsSelectable)  # Make non-selectable
                dir_widget = widgets.DirectoryListItem()
                dir_widget.set_data(str(current_dir))
                list_item.setSizeHint(dir_widget.sizeHint())
                self.view.list_sequences.addItem(list_item)
                self.view.list_sequences.setItemWidget(list_item, dir_widget)
            
            # Add the sequence item
            list_item = QtWidgets.QListWidgetItem()
            custom_widget = widgets.CustomListItem()
            custom_widget.set_data(
                name=image_file.name,
                type=image_file.extension.upper(),
                range=self.get_frame_range(image_file),
            )
            list_item.setSizeHint(custom_widget.sizeHint())
            self.view.list_sequences.addItem(list_item)
            self.view.list_sequences.setItemWidget(list_item, custom_widget)

    def get_frame_range(self, image_file: ImageFile) -> str:
        
        if image_file.frame_count > 1:
            return f"{image_file.first_frame()}-{image_file.last_frame()}"
        elif image_file.frame_count == -1:
            return "Unknown"
        else:
            return "Single Frame"

    def on_load_requested(self):
        
        # print(self._get_selected_image_files())
        for i in self._get_selected_image_files():
            ReadWrapper.from_image_file(i)
    
    def on_select_all_requested(self):
        """Handle select all request"""
        self.view.select_all()
        
    def on_deselect_all_requested(self):
        """Handle deselect all request"""
        self.view.deselect_all()
        
    def _get_selected_image_files(self) -> List[ImageFile]:
        """Get selected image files"""
        return [self.model._ImageFiles[i] for i in self.view.get_selected_indices()]
    
    def on_cancel_requested(self):
        """Handle cancel request"""
        self.view.close()
        
        
        
