from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import nuke

from nhp.pysequitur.file_sequence import FileSequence, SequenceFactory, Components
from nhp.pysequitur.file_types import MOVIE_FILE_TYPES

from enum import Enum, auto


class FileHandlerType(Enum):
    """Enumeration of possible file handler types."""

    MOVIE = auto()
    SEQUENCE = auto()
    SINGLE = auto()
    UNKNOWN = auto()


class ImageFile(ABC):
    """Base class for handling image files (both sequences and single images)"""

    def __init__(self, id: Optional[int] = None):
        self.id = id

    @staticmethod
    def from_path(path: Path, id=None) -> "MovieFile| SequenceFile | SingleFile":
        """Factory method to create appropriate handler"""
        print("ImageFile from path")
        extension = Path(path).suffix.lstrip(".").lower()

        if extension in MOVIE_FILE_TYPES:
            print("movie file")
            return MovieFile(Path(path))

        try:
            sequence = SequenceFactory.from_sequence_string_absolute(
                str(path), min_frames=1
            )
            # sequence = FileSequence.match_sequence_string_absolute(str(path), min_frames=1)
            if sequence:
                return SequenceFile(sequence)
            return SingleFile(Path(path))
        except ValueError:
            return SingleFile(Path(path))

    @staticmethod
    def from_file_sequence(file_seq: FileSequence, id: Optional[int] = None):
        sequence_file = SequenceFile(file_seq)
        sequence_file.id = id
        return sequence_file

    @abstractmethod
    def get_path(self) -> Path:
        """Return the path as a Path."""
        pass

    @abstractmethod
    def get_user_text(self) -> str:
        """Return a string compatible with read node fromUserText() method."""
        pass

    @abstractmethod
    def first_frame(self) -> int:
        """Return the first frame number."""
        pass

    @abstractmethod
    def last_frame(self) -> int:
        """Return the last frame number."""
        pass

    @abstractmethod
    def folderize(self, folder_name: str, virtual: bool = False) -> "ImageFile":
        """Move files to a new folder with the given name."""
        pass

    @abstractmethod
    def delete_files(self) -> None:
        """Delete the files from disk."""
        pass

    @abstractmethod
    def rename(self, components: Components, virtual: bool = False) -> "ImageFile":
        """Rename files according to components."""
        pass

    @abstractmethod
    def offset_frames(
        self, offset: int, node: nuke.Node, virtual: bool = False
    ) -> "ImageFile":  # type: ignore
        """Offset frame numbers by the given amount."""
        pass

    @abstractmethod
    def copy_to(
        self, components: Components, target_dir: Optional[Path], virtual: bool = False
    ) -> "ImageFile":
        """Copy files to a new location with optional new components."""
        pass

    @abstractmethod
    def move_to(
        self, new_directory: Path, create_directory: bool = False, virtual: bool = False
    ) -> "ImageFile":
        """Move files to a new location with optional new components."""
        pass

    @property
    @abstractmethod
    def directory(self) -> Path:
        """Return the directory containing the files."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the base name of the files."""
        pass

    @property
    @abstractmethod
    def extension(self) -> str:
        """Return the file extension."""
        pass

    @property
    @abstractmethod
    def frame_count(self) -> int:
        """Return the number of frames."""
        pass

    @property
    @abstractmethod
    def suffix(self) -> str:
        """Return the suffix part of the filename."""
        pass

    @property
    @abstractmethod
    def delimiter(self) -> str:
        """Return the frame number delimiter."""
        pass

    @property
    @abstractmethod
    def padding(self) -> int:
        """Return the padding of the filename."""
        pass


class SequenceFile(ImageFile):
    """Handler for file sequences"""

    def __init__(self, sequence: FileSequence):
        self.sequence = sequence

    def get_path(self) -> Path:
        return Path(self.sequence.absolute_file_name)

    def get_user_text(self) -> str:
        return f"{self.sequence.absolute_file_name} {self.sequence.first_frame}-{self.sequence.last_frame}"

    def first_frame(self) -> int:
        return self.sequence.first_frame

    def last_frame(self) -> int:
        return self.sequence.last_frame

    def folderize(self, folder_name: str, virtual: bool = False) -> "ImageFile":
        if virtual:
            return ImageFile.from_file_sequence(
                self.sequence.folderize(folder_name, virtual=virtual)
            )
        self.sequence.folderize(folder_name)
        return self

    def delete_files(self) -> "ImageFile":
        self.sequence.delete_files()
        return self

    def rename(self, components: Components, virtual: bool = False) -> "ImageFile":
        return ImageFile.from_file_sequence(
            self.sequence.rename_to(components, virtual=virtual)
        )

    def offset_frames(self, offset: int, node: nuke.Node, virtual: bool = False) -> "ImageFile":  # type: ignore
        if virtual:
            return ImageFile.from_file_sequence(
                self.sequence.offset_frames(offset, virtual=virtual)
            )
        self.sequence.offset_frames(offset)
        node["file"].setValue(self.get_path())
        node["first"].setValue(self.first_frame())
        node["origfirst"].setValue(self.first_frame())
        node["last"].setValue(self.last_frame())
        node["origlast"].setValue(self.last_frame())
        return self

    def copy_to(
        self, components: Components, target_dir: Optional[Path], virtual: bool = False
    ) -> "ImageFile":
        
        return ImageFile.from_file_sequence(
            self.sequence.copy_to(
                new_name=components, new_directory=target_dir if target_dir else None, virtual=virtual
            )
        )

    def move_to(
        self,
        new_directory: Path,
        create_directory: bool = False,
        virtual: bool = False
    ) -> "ImageFile":
        if virtual:
            return ImageFile.from_file_sequence(
                self.sequence.move_to(new_directory, create_directory=create_directory, virtual=virtual)
            )
        self.sequence.move_to(new_directory, create_directory=create_directory)
        return self

    @property
    def directory(self) -> Path:
        return Path(self.sequence.directory)

    @property
    def name(self) -> str:
        return self.sequence.prefix

    @property
    def extension(self) -> str:
        return self.sequence.extension

    @property
    def frame_count(self) -> int:
        return self.sequence.frame_count

    @property
    def suffix(self) -> str | None:
        return self.sequence.suffix

    @property
    def delimiter(self) -> str:
        return self.sequence.delimiter

    @property
    def padding(self) -> int:
        return self.sequence.padding


class SingleFile(ImageFile):
    """Handler for single image files"""

    def __init__(self, path: Path):
        print("init single file")
        self.path = path
        if not path.exists():
            raise ValueError(f"File {path} does not exist")

    def get_path(self) -> Path:
        return self.path

    def get_user_text(self) -> str:
        return str(self.path)

    def first_frame(self) -> int:
        return 1

    def last_frame(self) -> int:
        return 1

    def folderize(self, folder_name: str, virtual: bool = False) -> "ImageFile":
        folder_path = self.path.parent / folder_name
        folder_path.mkdir(exist_ok=True)
        new_path = folder_path / self.path.name

        if virtual:
            return ImageFile.from_path(new_path, self.id)
        self.path = self.path.rename(new_path)
        return self

    def delete_files(self) -> None:
        self.path.unlink()

    def rename(self, components: Components, virtual: bool = False) -> ImageFile:
        new_name = components.prefix or self.path.stem
        new_ext = components.extension or self.path.suffix.lstrip(".")
        new_path = self.path.parent / f"{new_name}.{new_ext}"

        if not virtual:
            self.path = self.path.rename(new_path)
            return self

        return ImageFile.from_path(new_path, self.id)

    def move_to(
        self, new_directory: Path, create_directory: bool = False, virtual: bool = False
    ) -> ImageFile:

        new_path = new_directory / self.path.name
    
        if virtual:
            return ImageFile.from_path(new_path, self.id)
    
        if create_directory:
            new_directory.mkdir(exist_ok=True, parents=True)

        self.path = self.path.rename(new_path)
        return self 

    def offset_frames(self, offset: int, node: nuke.Node, virtual: bool = False) -> "ImageFile":  # type: ignore
        # No-op for single files
        print("not supported for single files")
        return self

    def copy_to(
        self, components: Components, target_dir: Optional[Path], virtual: bool = False
    ) -> "ImageFile":
        import shutil

        target_dir = target_dir or self.path.parent
        target_dir.mkdir(exist_ok=True, parents=True)

        new_name = components.prefix or self.path.stem
        new_ext = components.extension or self.path.suffix.lstrip(".")
        new_path = target_dir / f"{new_name}.{new_ext}"
        if not virtual:
            shutil.copy2(self.path, new_path)
        return ImageFile.from_path(new_path, self.id)

    @property
    def directory(self) -> Path:
        return self.path.parent

    @property
    def name(self) -> str:
        return self.path.stem

    @property
    def extension(self) -> str:
        return self.path.suffix.lstrip(".")

    @property
    def frame_count(self) -> int:
        return 1

    @property
    def suffix(self) -> str:
        return ""

    @property
    def delimiter(self) -> str:
        return ""

    @property
    def padding(self) -> int:
        return 0


class MovieFile(SingleFile):
    """Handler for movie files that have multiple frames"""

    def __init__(self, path: Path):
        super().__init__(path)
        print("init movie file")
        self._first_frame = 1
        self._last_frame = -1  # Will be updated by ReadWrapper

    def get_user_text(self) -> str:
        # For movie files, we return just the path
        # The frame range will be set by the Read node in Nuke
        return str(self.path)

    def set_frame_range(self, first_frame: int, last_frame: int) -> "ImageFile":
        if not isinstance(first_frame, int):
            raise TypeError("first_frame must be an integer")

        if not isinstance(last_frame, int):
            raise TypeError("last_frame must be an integer")

        self._first_frame = first_frame
        self._last_frame = last_frame
        return self

    def copy_to(
        self, components: Components, target_dir: Optional[Path], virtual: bool = False
    ) -> "ImageFile":
        import shutil

        target_dir = target_dir or self.path.parent
        target_dir.mkdir(exist_ok=True, parents=True)

        new_name = components.prefix or self.path.stem
        new_ext = components.extension or self.path.suffix.lstrip(".")
        new_path = target_dir / f"{new_name}.{new_ext}"

        if not virtual:
            shutil.copy2(self.path, new_path)
        new_movie = MovieFile(new_path)
        new_movie.set_frame_range(self._first_frame, self._last_frame)
        return new_movie

    def offset_frames(self, offset: int, node: nuke.Node, virtual: bool = False) -> "ImageFile":  # type: ignore
        node["frame_mode"].getValue(2)
        k = node["frame"]
        k.setValue(str(int(k.getValue() or 0) + offset))
        return self

    @property
    def frame_count(self) -> int:
        return self._last_frame - self._first_frame + 1

    def rename(self, components: Components, virtual: bool = False) -> "ImageFile":
        return super().rename(components, virtual=virtual)

    def first_frame(self) -> int:
        return self._first_frame

    def last_frame(self) -> int:
        return self._last_frame


class ReadWrapper:
    """Wrapper for Read nodes with enhanced file handling capabilities"""

    def __init__(self, read_node: nuke.nodes.Read, handler: Optional[ImageFile] = None):  # type: ignore
        if not read_node.Class() == "Read":
            raise ValueError("read_node must be a nuke.nodes.Read node")

        self.read_node = read_node

        if not handler:
            print("init read wrapper, no handler")
            self.file_handler = ImageFile.from_path(read_node["file"].getValue())
        else:
            print("init read wrapper, handler")
            self.file_handler = handler

    @property
    def handler_type(self) -> FileHandlerType:
        """Returns the type of file handler as an enum value."""
        if isinstance(self.file_handler, MovieFile):
            return FileHandlerType.MOVIE
        elif isinstance(self.file_handler, SequenceFile):
            return FileHandlerType.SEQUENCE
        elif isinstance(self.file_handler, SingleFile):
            return FileHandlerType.SINGLE
        return FileHandlerType.UNKNOWN

    @classmethod
    def from_path(cls, abs_path: str, virtual: bool = False) -> "ReadWrapper":
        """Creates a read node from an absolute path"""
        path = Path(abs_path)
        if not path.parent.exists():
            raise ValueError(f"Directory {path.parent} does not exist")

        handler = ImageFile.from_path(path)

        if virtual:
            return cls(None, handler)

        read_node = nuke.createNode("Read")  # type: ignore
        read_node["file"].fromUserText(handler.get_user_text())

        if hasattr(handler, "set_frame_range"):
            handler.set_frame_range(  # type: ignore
                int(read_node["first"].getValue()), int(read_node["last"].getValue())
            )  # type: ignore

        return cls(read_node, handler)

    @classmethod
    def from_write(cls, source_node: nuke.Node) -> "ReadWrapper":  # type: ignore
        """Creates a read node from a write node"""
        # if "file" not in source_node.knobs():
        #     raise ValueError("Source node does not have a file knob")

        if not source_node.Class() == "Write":
            raise ValueError("Source node must be a Write node")

        read_wrapper = cls.from_path(source_node["file"].getValue())

        read_wrapper.read_node.setXYpos(
            int(source_node["xpos"].getValue()),
            int(source_node["ypos"].getValue()) + 50,
        )

        return read_wrapper

    @classmethod
    def from_file_sequence(cls, file_seq: FileSequence):
        handler = ImageFile.from_file_sequence(file_seq)
        read_node = nuke.createNode("Read")  # type: ignore
        read_node["file"].fromUserText(handler.get_user_text())
        return cls(read_node, handler)

    @classmethod
    def from_image_file(cls, image_file: ImageFile) -> "ReadWrapper":
        read_node = nuke.createNode("Read")  # type: ignore
        read_node["file"].fromUserText(image_file.get_user_text())
        return cls(read_node, image_file)

    def folderize(self) -> "ReadWrapper":
        """Creates a folder with the same name as the sequence/file and moves files into it"""
        new_path = self.file_handler.folderize(self.file_handler.name)
        self.read_node["file"].setValue(new_path)
        return self

    def delete(self, delete_node=False):
        """Deletes the files and optionally the node"""
        self.file_handler.delete_files()

        if delete_node:
            nuke.delete(self.read_node)  # type: ignore
        else:
            self.read_node["tile_color"].setValue(4278190335)  # Red

        return self

    def move(
        self,
        target_dir: Path,
        create_directory: bool = False,
    ) -> "ReadWrapper":
        new_path = self.file_handler.move_to(target_dir, create_directory)
        self.read_node["file"].setValue(new_path)
        return self

    def rename(
        self,
        name: Optional[str] = None,
        delimiter: Optional[str] = None,
        padding: Optional[int] = None,
        suffix: Optional[str] = None,
        extension: Optional[str] = None,
        preview=False,
    ) -> "ReadWrapper":
        """Renames the file/sequence and reconnects the node"""
        components = Components(
            prefix=name,
            delimiter=delimiter,
            padding=padding,
            suffix=suffix,
            extension=extension,
        )

        if preview:
            new_path = self.file_handler.rename(components, virtual=True)
            print(new_path)
            return ReadWrapper.from_path(new_path, virtual=True)

        new_path = self.file_handler.rename(components)
        self.read_node["file"].setValue(new_path)
        return self

    def offset(self, offset: int) -> "ReadWrapper":
        """Offset the frame numbers in the sequence (no-op for single files)"""
        self.file_handler.offset_frames(offset, self.read_node)

        # Update node
        # self.read_node["file"].setValue(self.file_handler.get_path())
        # self.read_node["first"].setValue(self.file_handler.first_frame())
        # self.read_node["origfirst"].setValue(self.file_handler.first_frame())
        # self.read_node["last"].setValue(self.file_handler.last_frame())
        # self.read_node["origlast"].setValue(self.file_handler.last_frame())

        return self

    def set_first_frame(self, frame: int) -> "ReadWrapper":
        """Sets the first frame of the sequence (no-op for single files)"""
        if hasattr(self.file_handler, "sequence"):  # It's a sequence file
            offset = frame - self.file_handler.first_frame()
            return self.offset(offset)
        return self

    def copy(
        self,
        name: Optional[str] = None,
        delimiter: Optional[str] = None,
        padding: Optional[int] = None,
        suffix: Optional[str] = None,
        extension: Optional[str] = None,
        directory: Optional[str] = None,
        create_directory: bool = False,
    ) -> "ReadWrapper":
        """Creates a copy with optional new name/location and returns a new wrapper"""
        dir_path = None
        if directory:
            dir_path = Path(directory)
            if not dir_path.exists():
                if create_directory:
                    dir_path.mkdir(parents=True)
                else:
                    raise ValueError(f"Directory {directory} does not exist")

        components = Components(
            prefix=name,
            delimiter=delimiter,
            padding=padding,
            suffix=suffix,
            extension=extension,
        )

        new_handler = self.file_handler.copy_to(components, dir_path)

        read_node = nuke.createNode("Read")  # type: ignore

        read_node["file"].fromUserText(new_handler.get_user_text())

        return ReadWrapper(read_node)

    # Properties that delegate to the handler
    @property
    def directory(self) -> Path:
        return self.file_handler.directory

    @property
    def first_frame(self) -> int:
        return self.file_handler.first_frame()

    @property
    def last_frame(self) -> int:
        return self.file_handler.last_frame()

    @property
    def frame_count(self) -> int:
        return self.file_handler.frame_count

    @property
    def name(self) -> str:
        return self.file_handler.name

    @property
    def extension(self) -> str:
        return self.file_handler.extension

    @property
    def suffix(self) -> str | None:
        return self.file_handler.suffix

    @property
    def delimiter(self) -> str:
        return self.file_handler.delimiter

    @property
    def padding(self) -> int:
        return self.file_handler.padding

    @classmethod
    def from_read(cls, source_node: nuke.Node) -> "ReadWrapper":  # type: ignore
        """Creates a read wrapper from a read node"""
        return cls(source_node)


def node_from_sequence_string(sequence_string: str) -> nuke.Node:  # type: ignore
    """Utility function to create a Read node from a path"""
    wrapper = ReadWrapper.from_path(sequence_string)
    return wrapper.read_node
