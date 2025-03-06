from typing import List
from nhp.read_tools.read_wrapper import ImageFile, SequenceFile
from pysequitur.crawl import Node


# def generate_read_nodes(node: Node):
    
#     print(node.path)
#     # print(node.movies)
#     # print(node.sequences)
#     # print(node.rogues)
#     # print(node.dirs) 
    
#     image_sequences: list[SequenceFile] = [ImageFile.from_file_sequence(sequence) for sequence in node.sequences]
#     mov_files: list[ImageFile] = [ImageFile.from_path(movie) for movie in node.movies]
#     rogue_files: list[ImageFile] = [ImageFile.from_path(rogue) for rogue in node.rogues]
    
#     print(image_sequences + mov_files + rogue_files)
    
#     for node in node.nodes:
#         generate_read_nodes(node)


def generate_read_nodes_2(sequences: List[ImageFile]):
    for sequence in sequences:
        print(sequence.get_path())