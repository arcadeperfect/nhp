from pathlib import Path

from pysequitur import integrations, file_sequence, Components


import nuke

class ReadWrapper:
    def __init__(self, read_node: nuke.nodes.Read):
        if not read_node.Class() == "Read":
            raise ValueError("read_node must be a nuke.nodes.Read node")
        self.read_node = read_node
        self.file_sequence = file_sequence.FileSequence.match_sequence_string_absolute(self.read_node['file'].getValue())
        if not self.file_sequence:
            raise ValueError("Failed to parse file sequence from read node")
        
        
    def folderize(self) -> "ReadWrapper":
        
        """
        Creates a folder with the same name as the sequence and moves the files into it

        Returns:
            ReadWrapper: Self for method chaining

        Raises:
            ValueError: FileSequence not found in this class instance
        """
        
        if not self.file_sequence:
            raise ValueError("No file sequence found")
        
        self.file_sequence.folderize(self.file_sequence.prefix)
    
        current_path = Path(self.read_node['file'].getValue())
        new_path = current_path.parent / self.file_sequence.prefix / current_path.name
    
        self.read_node['file'].setValue(
            new_path.as_posix()
        )
        
        return self

    def delete(self, delete_node = False) -> "ReadWrapper":
        
        """
        Deletes the files and optionally the node
        
        Returns: 
            ReadWrapper: Self for method chaining
        
        Raises:
            ValueError: FileSequence not found in this class instance
        """
        
        if not self.file_sequence:
            raise ValueError("No file sequence found")
        
        self.file_sequence.delete_files()
        
        if delete_node:
            nuke.delete(self.read_node)
        
        else:
            self.read_node['tile_color'].setValue(4278190335)
            
    
    def rename(self, 
               new_name: str | None = None, 
               delimiter: str | None = None, 
               padding: int | None = None, 
               suffix: str | None = None, 
               extension: str | None = None
               ) -> "ReadWrapper":
        """
        Renames the file sequence and reconnects the node.
        
        Returns: 
            ReadWrapper: Self for method chaining
        
        Raises:
            ValueError: _description_
        """    
        
        if not self.file_sequence:
            raise ValueError("No file sequence found")
        
        
        
        self.file_sequence.rename_to(
            Components(prefix = new_name, delimiter = delimiter, padding = padding, suffix = suffix, extension = extension)
        )
        
        self.read_node['file'].setValue(
            self.file_sequence.absolute_file_name
        )
        
        return self
        
        
    def offset_frames(self, offset: int):
        """
        Offset the frame numbers in the sequence by the given amount and
        update the Read node path.
        
        Args:
            offset (int): The frame offset to apply (positive or negative)
            padding (int, optional): New padding for frame numbers
        
        Returns:
            ReadWrapper: Self for method chaining
            
        Raises:
            ValueError: If FileSequence not found or offset would result in negative frame numbers
        """
        
        if not self.file_sequence:
            raise ValueError("No file sequence found")
        
        self.file_sequence.offset_frames(offset)
        
        self.read_node['file'].setValue(
            self.file_sequence.absolute_file_name
        )
        
        self.read_node['first'].setValue(
            self.file_sequence.first_frame
        )
        self.read_node['origfirst'].setValue(
            self.file_sequence.first_frame
        )
        
        self.read_node['last'].setValue(
            self.file_sequence.last_frame
        )
        
        self.read_node['origlast'].setValue(
            self.file_sequence.last_frame
        )
        
        return self
    
    
    def set_first_frame(self, frame: int):
    
        """
        Renames the files in the sequence to start at the given frame number and updates the node.
        
        Returns:
            ReadWrapper: Self for method chaining
            
        Raises:
            ValueError: If FileSequence not found or offset would result in negative frame numbers
        """
        
        if not self.file_sequence:
            raise ValueError("No file sequence found")
        
        return self.offset_frames(frame - self.file_sequence.first_frame)
    
    def copy(self, 
             name: str | None = None, 
             delimiter: str | None = None, 
             padding: int | None = None, 
             suffix: str | None = None, 
             extension: str | None = None,
             directory: str | None = None,
             create_directory: bool = False
             ):
        
        if not self.file_sequence:
            raise ValueError("No file sequence found")
        
        if directory is not None:
            directory = Path(directory)
            if not directory.exists():
                if create_directory:
                    directory.mkdir(parents = True)
                else:
                    raise ValueError(f"Directory {directory} does not exist")
                
        
        return self.file_sequence.copy_to(
            new_name = Components(prefix = name, delimiter = delimiter, padding = padding, suffix = suffix, extension = extension), 
            new_directory = directory
        )
        
             
    @property
    def directory(self):
        return self.file_sequence.directory
