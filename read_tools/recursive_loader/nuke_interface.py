from pathlib import Path
from typing import List
from nhp.read_tools.read_wrapper import ImageFile, ReadWrapper, SequenceFile
from pysequitur.crawl import Node
import nuke
import nukescripts

COLOR_1 = 948866560
COLOR_2 = 16777215

def backdrop(nodes: list[nuke.Node], path: str, count: int):


    color = COLOR_1 if count % 2 == 0 else COLOR_2

    
    nuke.selectAll()
    nuke.invertSelection()
    for node in nodes:
        node['selected'].setValue(True)
    b = nukescripts.autoBackdrop()
    b['label'].setValue(path)
    b['note_font_size'].setValue(30)
    nuke.selectAll()
    nuke.invertSelection()
    resize_backdrop_to_fit_label(b)
    b['tile_color'].setValue(color)

def generate_read_nodes_2(sequences: List[ImageFile]):

    if len(sequences) == 0:
        return
        
    write_nodes: dict[Path, list[nuke.Node]] = {} # type: ignore
    
    for sequence in sequences:
        path = sequence.get_path().parent
        wrapper = ReadWrapper.from_image_file(sequence)
        node = wrapper.read_node
        if path not in write_nodes.keys():
            write_nodes[path] = []
        write_nodes[path].append(node)


    # for path, nodes in write_nodes.items():
    #     print(path)
    #     for n in nodes:
    #         print(n.name())

    # return

    try:
        first_node = list(write_nodes.values())[0][0]
    except Exception as e:
        print(f"no write nodes were created: {e}")
        return
    
    
    origin = first_node['xpos'].getValue(), first_node['ypos'].getValue()
    
    offset = (100, 200)
    
    xcount = 0
    ycount = 0
    count = 0
    for path, nodes in write_nodes.items():
        for node in nodes:
            node['xpos'].setValue(origin[0] + xcount * offset[0])
            node['ypos'].setValue(origin[1] + ycount * offset[1])
            xcount += 1
        backdrop(nodes, path.as_posix(), count)
        xcount = 0
        ycount += 1
        count += 1
            

    
    
    
def resize_backdrop_to_fit_label(backdrop_node):
    """
    Resizes a backdrop to fit its label text content
    Args:
        backdrop_node: The backdrop node to resize
    """
    # Get the label text
    label = backdrop_node['label'].value()
    
    # Create a temporary Text_Knob to calculate dimensions
    temp_text = nuke.Text_Knob('temp_text', '')
    temp_text.setLabel(label)
    

    font_width_approx = 7  # Average width of a character in pixels

    
    # Count lines and max line length
    lines = label.split('\n')
    max_chars = max([len(line) for line in lines])

    
    # Calculate dimensions with some padding
    text_width = max_chars * font_width_approx

    
    # Add padding
    padding_x = 20

    new_value = text_width * 2 + 2 * padding_x
    if new_value < backdrop_node['bdwidth'].getValue():
        return
        
    # Set the new dimensions
    backdrop_node['bdwidth'].setValue(text_width * 2 + 2 * padding_x)