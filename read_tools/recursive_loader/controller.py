from pathlib import Path
from typing import List
from PySide2 import QtWidgets, QtCore
from nhp.read_tools.read_wrapper import ImageFile, MovieFile, ReadWrapper
from nhp.read_tools.recursive_loader.view import View
from nhp.read_tools.recursive_loader.model import Model


class Controller:
    def __init__(self, view: View, model: Model):
        print("controller init 2")
        self.view = view
        self.model = model

        # Connect signals
        self.view.directory_selected.connect(self.on_directory_selected)
        self.view.scan_requested.connect(self.on_scan_requested)
        self.view.load_requested.connect(self.on_load_requested)
        self.view.select_all_requested.connect(self.on_select_all_requested)
        self.view.cancel_requested.connect(self.on_cancel_requested)

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
        self.populate_list()

    def on_select_all_requested(self):
        """Handle select all request"""
        self.view.select_all()

    def on_cancel_requested(self):
        """Handle cancel request"""
        self.view.close()

    def populate_list(self):
        """Populate the lists with the sequences"""
        self.view.clear_list()
        
        base_dir = self.model.current_directory
        if not base_dir:
            return
        
        # First, organize files by directory
        dir_files: dict[str, list[ImageFile]] = {}
        for image_file in self.model._ImageFiles:
            rel_path = str(image_file.directory.relative_to(base_dir))
            if rel_path not in dir_files:
                dir_files[rel_path] = []
            dir_files[rel_path].append(image_file)
        
        # Build directory tree structure
        class DirNode:
            def __init__(self, name, path):
                self.name = name
                self.path = path
                self.subdirs: list[DirNode] = []
                self.files: list[ImageFile] = []
        
        # Create root node
        root = DirNode("", "")
        
        # Build the tree structure
        for dir_path, files in dir_files.items():
            if not dir_path:  # Root directory
                root.files = files
                continue
            
            parts = Path(dir_path).parts
            current = root
            
            # Create path in tree
            for i, part in enumerate(parts):
                # Find or create subdirectory
                found = False
                for subdir in current.subdirs:
                    if subdir.name == part:
                        current = subdir
                        found = True
                        break
                
                if not found:
                    path = str(Path(*parts[:i+1]))
                    new_node = DirNode(part, path)
                    current.subdirs.append(new_node)
                    current = new_node
            
            # Add files to the current directory
            current.files = files
        
        # Now recursively display the tree
        def display_tree(dir_node: DirNode, prefix="", is_last=True):
            # Skip displaying root directory
            if dir_node.name:
                self.view.add_row(
                    f"{prefix}{'└── ' if is_last else '├── '}{dir_node.name}/",
                    "",
                    "",
                    "",
                    "",
                    selectable=False
                )
            
            # Create new prefix for children
            new_prefix = prefix
            if dir_node.name:  # Not for root
                new_prefix = prefix + ("    " if is_last else "│   ")
            
            # Process subdirectories first
            for i, subdir in enumerate(sorted(dir_node.subdirs, key=lambda x: x.name)):
                is_last_dir = i == len(dir_node.subdirs) - 1
                is_last_item = is_last_dir and not dir_node.files
                display_tree(subdir, new_prefix, is_last_item)
            
            # Then process files
            for i, file in enumerate(dir_node.files):
                is_last_file = i == len(dir_node.files) - 1
                file_prefix = new_prefix + ("└── " if is_last_file else "├── ")
                
                self.view.add_row(
                    f"{file_prefix}[{self.get_display_type(file)}]",
                    file.name,
                    file.extension,
                    self.get_frame_range(file),
                    file.get_path()
                )     
        
        
        # Start display from root
        display_tree(root)

    

    def get_frame_range(self, image_file: ImageFile) -> str:
        """Get frame range string for an image file"""
        if image_file.frame_count > 1:
            return f"{image_file.first_frame()}-{image_file.last_frame()}"
        elif image_file.frame_count == -1:
            return "Unknown"
        else:
            return "Single Frame"

    def on_load_requested(self):
        """Handle load request"""
        try:
            selected_files = self._get_selected_image_files()
            if not selected_files:
                self.view.show_info("No items selected")
                return
                
            for image_file in selected_files:
                ReadWrapper.from_image_file(image_file)
                
            self.view.show_info(f"Created {len(selected_files)} read nodes")
        except Exception as e:
            self.view.show_error(f"Failed to create nodes: {str(e)}")

    def _get_selected_image_files(self) -> List[ImageFile]:
        """Get ImageFiles for selected items"""
        selected_indices = self.view.get_selected_indices()
        return [self.model.get_sequence(idx) for idx in selected_indices]
    
    def get_display_type(self, image_file: ImageFile) -> str:
        """Get display type for an image file"""
        if isinstance(image_file, MovieFile):
            return "MOV"
        elif image_file.frame_count > 1:
            return "SEQ"
        else:
            return "IMG"