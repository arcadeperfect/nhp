from pathlib import Path
from nhp.read_tools.lib import ImageFile
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
        self.model.scan_directory(self.view.get_path_text())
        crawl.visualize_tree(self.model._node)
        self.populate_list()

    
    
    def populate_list(self):
        
        """Populate the list with the sequences"""
        # Clear existing items
        self.view.clear_list()
        
        for i, image_file in enumerate(self.model._ImageFiles):
       
       
            list_item = QtWidgets.QListWidgetItem() 
            custom_widget = widgets.CustomListItem()
            custom_widget.set_data(image_file.name)
            list_item.setSizeHint(custom_widget.sizeHint())
            
            self.view.list_sequences.addItem(list_item)
            self.view.list_sequences.setItemWidget(list_item, custom_widget)
       