from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import pysequitur
from pysequitur import crawl
from pysequitur.crawl import Node
from nhp.read_tools.read_wrapper import ImageFile


@dataclass
class DirectoryTree:
    """Represents a directory in the file system with its contents"""
    name: str
    path: str
    subdirs: List['DirectoryTree']
    files: List[ImageFile]

    @classmethod
    def build_from_files(cls, files: List[ImageFile], base_dir: Path) -> 'DirectoryTree':
        """Build a directory tree from a list of files"""
        # Create root node
        root = cls("", "", [], [])
        
        # First, organize files by directory
        dir_files: dict[str, List[ImageFile]] = {}
        for image_file in files:
            rel_path = str(image_file.directory.relative_to(base_dir))
            if rel_path not in dir_files:
                dir_files[rel_path] = []
            dir_files[rel_path].append(image_file)
        
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
                    new_node = cls(part, path, [], [])
                    current.subdirs.append(new_node)
                    current = new_node
            
            # Add files to the current directory
            current.files = files
            
        return root


class Model:
    def __init__(self):
        self._ImageFiles: List[ImageFile] = []
        self._current_directory: Optional[Path] = None
        self._node: Optional[Node] = None
        self._display_order: List[ImageFile] = []  #
        self.ImageFileById: dict[int, ImageFile] = {}

    def scan_directory(self, directory: Path) -> None:
        """Scan directory for sequences"""
        self._current_directory = directory
        self._ImageFiles.clear()
        self._display_order.clear()
        
        root_node = pysequitur.crawl.recursive_scan(directory)
        crawl.visualize_tree(root_node)
        
        id = 0
        
        # First collect all files
        for results in crawl.traverse_nodes(root_node):
            for sequence in results.sequences:
                image_file = ImageFile.from_file_sequence(sequence)
                image_file.id = id
                self._ImageFiles.append(image_file)
                self.ImageFileById[id] = image_file
                id += 1
            for movie in results.movs:
                image_file = ImageFile.from_path(movie)
                image_file.id = id
                self._ImageFiles.append(image_file)
                self.ImageFileById[id] = image_file
                id += 1
                # self._ImageFiles.append(ImageFile.from_path(movie))
            for rogue in results.rogues:
                image_file = ImageFile.from_path(rogue)
                image_file.id = id
                self._ImageFiles.append(image_file)
                self.ImageFileById[id] = image_file
                id += 1
                # self._ImageFiles.append(ImageFile.from_path(rogue))
            
        # Then sort them by directory to match display order
        self._display_order = sorted(self._ImageFiles, key=lambda x: str(x.get_path()))
        self._node = root_node

    def build_directory_tree(self) -> Optional[DirectoryTree]:
        """Build a directory tree from the current files"""
        if not self._current_directory or not self._ImageFiles:
            return None
        return DirectoryTree.build_from_files(self._ImageFiles, self._current_directory)

    def get_sequence(self, index: int) -> ImageFile:
        """Get sequence at specific index"""
        return self._display_order[index]
    
    def get_all_sequences(self) -> List[ImageFile]:
        """Get all found sequences in display order"""
        return self._display_order
        
    def clear(self) -> None:
        """Clear all sequences"""
        self._ImageFiles.clear()
        self._current_directory = None
        
    @property
    def current_directory(self) -> Optional[Path]:
        """Get current directory being scanned"""
        return self._current_directory
    
    @property
    def sequence_count(self) -> int:
        """Get number of sequences found"""
        return len(self._ImageFiles)