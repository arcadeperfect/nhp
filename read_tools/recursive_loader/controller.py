from pathlib import Path
from typing import List
from PySide2 import QtWidgets, QtCore
from nhp.read_tools.read_wrapper import ImageFile, ReadWrapper
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
        dir_files = {}
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
                self.subdirs = []
                self.files = []
        
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
        def display_tree(node, prefix="", is_last=True):
            # Skip displaying root directory
            if node.name:
                dir_item_name = QtWidgets.QListWidgetItem(f"{prefix}{'└── ' if is_last else '├── '}{node.name}/")
                dir_item_type = QtWidgets.QListWidgetItem("")
                dir_item_range = QtWidgets.QListWidgetItem("")
                
                # Make directory items non-selectable
                for item in [dir_item_name, dir_item_type, dir_item_range]:
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
                
                self.view.list_names.addItem(dir_item_name)
                self.view.list_types.addItem(dir_item_type)
                self.view.list_ranges.addItem(dir_item_range)
            
            # Create new prefix for children
            new_prefix = prefix
            if node.name:  # Not for root
                new_prefix = prefix + ("    " if is_last else "│   ")
            
            # Process subdirectories first
            for i, subdir in enumerate(sorted(node.subdirs, key=lambda x: x.name)):
                is_last_dir = i == len(node.subdirs) - 1
                is_last_item = is_last_dir and not node.files
                display_tree(subdir, new_prefix, is_last_item)
            
            # Then process files
            for i, file in enumerate(node.files):
                is_last_file = i == len(node.files) - 1
                file_prefix = new_prefix + ("└── " if is_last_file else "├── ")
                
                file_name = f"{file_prefix}[{file.extension.upper()}] {file.name}"
                
                self.view.list_names.addItem(file_name)
                self.view.list_types.addItem(file.extension.upper())
                self.view.list_ranges.addItem(self.get_frame_range(file))
        
        # Start display from root
        display_tree(root)

    # def populate_list(self):
    #     """Populate the lists with the sequences"""
    #     self.view.clear_list()
        
    #     base_dir = self.model.current_directory
    #     if not base_dir:
    #         return
        
    #     # Step 1: Organize files into a tree structure for easier display
    #     file_tree = {}
    #     for image_file in self.model._ImageFiles:
    #         rel_path = image_file.directory.relative_to(base_dir)
    #         path_str = str(rel_path)
            
    #         if path_str not in file_tree:
    #             file_tree[path_str] = []
    #         file_tree[path_str].append(image_file)
        
    #     # Sort the directories
    #     sorted_dirs = sorted(file_tree.keys())
        
    #     # Step 2: Prepare prefix lines for each directory level
    #     prefix_map = {}  # Maps directory paths to their prefixes
        
    #     # Initialize root directory prefix
    #     prefix_map[""] = ""
        
    #     # For each directory, determine if it's the last at its level
    #     for i, dir_path in enumerate(sorted_dirs):
    #         parts = Path(dir_path).parts
    #         parent_path = str(Path(*parts[:-1])) if parts else ""
            
    #         # Is this the last directory at this level?
    #         is_last = True
    #         if i < len(sorted_dirs) - 1:
    #             next_parts = Path(sorted_dirs[i + 1]).parts
    #             # Check if the next directory is at the same level with same parent
    #             if len(next_parts) >= len(parts) and next_parts[:len(parts)-1] == parts[:len(parts)-1]:
    #                 is_last = False
            
    #         # Get parent prefix and extend it
    #         parent_prefix = prefix_map.get(parent_path, "")
            
    #         # Create this directory's prefix
    #         if parent_path:  # Not root
    #             if is_last:
    #                 # Last item at this level, use corner
    #                 my_prefix = parent_prefix + "└── "
    #                 # For children, replace the last "└──" with spaces
    #                 child_prefix = parent_prefix + "    "
    #             else:
    #                 # Not last, use T-shape
    #                 my_prefix = parent_prefix + "├── "
    #                 # For children, continue vertical line
    #                 child_prefix = parent_prefix + "│   "
    #         else:
    #             my_prefix = ""
    #             child_prefix = ""
            
    #         prefix_map[dir_path] = child_prefix
            
    #         # Step 3: Add directory to the list
    #         # Handle root directory (which has no parts) separately
    #         if parts:
    #             dir_name = parts[-1]
    #             dir_item_name = QtWidgets.QListWidgetItem(f"{my_prefix}{dir_name}/")
    #             dir_item_type = QtWidgets.QListWidgetItem("")
    #             dir_item_range = QtWidgets.QListWidgetItem("")
                
    #             # Make directory items non-selectable
    #             for item in [dir_item_name, dir_item_type, dir_item_range]:
    #                 item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
                
    #             self.view.list_names.addItem(dir_item_name)
    #             self.view.list_types.addItem(dir_item_type)
    #             self.view.list_ranges.addItem(dir_item_range)
            
    #         # Step 4: Add files for this directory
    #         files = file_tree[dir_path]
    #         for j, image_file in enumerate(files):
    #             is_last_file = j == len(files) - 1
                
    #             if is_last_file:
    #                 file_prefix = child_prefix + "└── "
    #             else:
    #                 file_prefix = child_prefix + "├── "
                
    #             name_text = f"{file_prefix}[{image_file.extension.upper()}] {image_file.name}"
                
    #             self.view.list_names.addItem(name_text)
    #             self.view.list_types.addItem(image_file.extension.upper())
    #             self.view.list_ranges.addItem(self.get_frame_range(image_file))


    # def populate_list(self):
    #     """Populate the lists with the sequences"""
    #     self.view.clear_list()
        
    #     base_dir = self.model.current_directory
    #     if not base_dir:
    #         return
        
    #     current_dir = None
    #     last_depth = 0
    #     is_last_at_depth = {}  # Track if item is last at each depth level
        
    #     # First pass to determine which directories are last at their depth
    #     for i, image_file in enumerate(self.model._ImageFiles):
    #         rel_path = image_file.directory.relative_to(base_dir)
    #         parts = rel_path.parts
            
    #         # For each directory in the path, check if it's the last one at its depth
    #         for depth in range(1, len(parts) + 1):
    #             parent_path = Path(*parts[:depth])
                
    #             # Check if this is the last directory at this depth by looking ahead
    #             is_last = True
    #             for j in range(i + 1, len(self.model._ImageFiles)):
    #                 next_file = self.model._ImageFiles[j]
    #                 next_parts = next_file.directory.relative_to(base_dir).parts
                    
    #                 if len(next_parts) >= depth and next_parts[:depth] != parts[:depth]:
    #                     is_last = False
    #                     break
                        
    #             is_last_at_depth[(parent_path, depth)] = is_last
        
    #     # Also determine if each file is the last in its directory
    #     file_is_last = {}
    #     for i, image_file in enumerate(self.model._ImageFiles):
    #         # Check if this is the last file in its directory
    #         is_last = True
    #         if i < len(self.model._ImageFiles) - 1:
    #             next_file = self.model._ImageFiles[i + 1]
    #             if next_file.directory == image_file.directory:
    #                 is_last = False
    #         file_is_last[image_file] = is_last
        
    #     # Second pass to populate the list
    #     displayed_dirs = set()  # Track directories we've already displayed
        
    #     for image_file in self.model._ImageFiles:
    #         rel_path = image_file.directory.relative_to(base_dir)
    #         parts = rel_path.parts
            
    #         # If we encounter a new directory, add a directory header
    #         if image_file.directory not in displayed_dirs:
    #             displayed_dirs.add(image_file.directory)
                
    #             # Display each directory level with proper indentation
    #             for depth in range(1, len(parts) + 1):
    #                 current_path = Path(*parts[:depth])
    #                 parent_path = Path(*parts[:depth-1]) if depth > 1 else None
                    
    #                 # Skip if we've already displayed this directory
    #                 if current_path in displayed_dirs:
    #                     continue
    #                 displayed_dirs.add(current_path)
                    
    #                 # Build the prefix with proper pipes
    #                 prefix = ""
    #                 for d in range(depth - 1):
    #                     path_to_check = Path(*parts[:d+1])
    #                     is_last = is_last_at_depth.get((path_to_check, d+1), True)
    #                     prefix += "    " if is_last else "│   "
                    
    #                 is_last_dir = is_last_at_depth.get((current_path, depth), True)
    #                 prefix += "└── " if is_last_dir else "├── "
                    
    #                 dir_name = parts[depth-1]
    #                 dir_item_name = QtWidgets.QListWidgetItem(f"{prefix}{dir_name}/")
    #                 dir_item_type = QtWidgets.QListWidgetItem("")
    #                 dir_item_range = QtWidgets.QListWidgetItem("")
                    
    #                 # Make directory items non-selectable
    #                 for item in [dir_item_name, dir_item_type, dir_item_range]:
    #                     item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
                    
    #                 self.view.list_names.addItem(dir_item_name)
    #                 self.view.list_types.addItem(dir_item_type)
    #                 self.view.list_ranges.addItem(dir_item_range)
            
    #         # Build the prefix for files with proper pipes
    #         prefix = ""
    #         for d in range(len(parts)):
    #             path_to_check = Path(*parts[:d+1])
    #             is_last = is_last_at_depth.get((path_to_check, d+1), True)
    #             prefix += "    " if is_last else "│   "
            
    #         # Add connector for the file (├── or └── if last file)
    #         is_last_file = file_is_last[image_file]
    #         prefix += "└── " if is_last_file else "├── "
            
    #         # Add the sequence items with proper indentation
    #         name_text = f"{prefix}[{image_file.extension.upper()}] {image_file.name}"
            
    #         self.view.list_names.addItem(name_text)
    #         self.view.list_types.addItem(image_file.extension.upper())
    #         self.view.list_ranges.addItem(self.get_frame_range(image_file))

    # def populate_list(self):
    #     """Populate the lists with the sequences"""
    #     self.view.clear_list()
        
    #     base_dir = self.model.current_directory
    #     if not base_dir:
    #         return
        
    #     current_dir = None
    #     for image_file in self.model._ImageFiles:
    #         # Calculate relative path
    #         rel_path = image_file.directory.relative_to(base_dir)
            
    #         # If we encounter a new directory, add a directory header
    #         if current_dir != image_file.directory:
    #             current_dir = image_file.directory
    #             dir_item_name = QtWidgets.QListWidgetItem(str(rel_path))
    #             dir_item_type = QtWidgets.QListWidgetItem("")
    #             dir_item_range = QtWidgets.QListWidgetItem("")
                
    #             # Make directory items non-selectable
    #             for item in [dir_item_name, dir_item_type, dir_item_range]:
    #                 item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
                
    #             self.view.list_names.addItem(dir_item_name)
    #             self.view.list_types.addItem(dir_item_type)
    #             self.view.list_ranges.addItem(dir_item_range)
            
    #         # Add the sequence items
    #         self.view.list_names.addItem(image_file.name)
    #         self.view.list_types.addItem(image_file.extension.upper())
    #         self.view.list_ranges.addItem(self.get_frame_range(image_file))

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