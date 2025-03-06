from typing import List, Tuple
from pathlib import Path
import pysequitur
from pysequitur import crawl
from nhp.read_tools.read_wrapper import ImageFile, ReadWrapper


class Model:
    def __init__(self):
        self._ImageFiles: List[ImageFile] = []
        self._current_directory: Path | None = None
        self._node = None
        
    def scan_directory(self, directory: Path) -> None:
        """Scan directory for sequences"""
        self._current_directory = directory
        self._ImageFiles.clear()
        
        if not isinstance(directory, Path):
            directory = Path(directory)
        
        root_node = pysequitur.crawl.recursive_scan(directory)
        # return
        
        crawl.visualize_tree(root_node)
        
        for results in crawl.traverse_nodes(root_node):
            for sequence in results.sequences:
                self._ImageFiles.append(ImageFile.from_file_sequence(sequence))
            for movie in results.movs:
                self._ImageFiles.append(ImageFile.from_path(movie))
            for rogue in results.rogues:
                self._ImageFiles.append(ImageFile.from_path(rogue))
            
        self._node = root_node
        
            
    def get_sequence(self, index: int) -> ImageFile:
        """Get sequence at specific index"""
        return self._ImageFiles[index]
    
    def get_all_sequences(self) -> List[ImageFile]:
        """Get all found sequences"""
        return self._ImageFiles
        
    def clear(self) -> None:
        """Clear all sequences"""
        self._ImageFiles.clear()
        self._current_directory = None
        
    @property
    def current_directory(self) -> Path | None:
        """Get current directory being scanned"""
        return self._current_directory
    
    @property
    def sequence_count(self) -> int:
        """Get number of sequences found"""
        return len(self._ImageFiles)