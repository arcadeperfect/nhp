from pathlib import Path
from typing import List, Optional
from nhp.read_tools.read_wrapper import ImageFile, ReadWrapper
import nuke
import nukescripts # type: ignore

COLOR_1 = 948866560
COLOR_2 = 16777215


def backdrop(nodes: list[nuke.Node], path: str, count: int) -> nuke.Node:  # type: ignore
    color = COLOR_1 if count % 2 == 0 else COLOR_2

    nuke.selectAll()  # type: ignore
    nuke.invertSelection()  # type: ignore
    for node in nodes:
        node["selected"].setValue(True)
    backdrop = nukescripts.autoBackdrop()
    backdrop["label"].setValue(path)
    backdrop["note_font_size"].setValue(30)
    nuke.selectAll()  # type: ignore
    nuke.invertSelection()  # type: ignore
    resize_backdrop_to_fit_label(backdrop)
    backdrop["tile_color"].setValue(color)

    return backdrop


def generate_read_nodes_2(
    sequences: List[ImageFile], count, origin: Optional[tuple[int, int]]
) -> tuple[tuple[int, int], int]:
    """
    Generate read nodes from a list of image files
    Args:
        sequences: List of ImageFile objects
        count: Current count of backdrop nodes
        origin: Optional tuple of int, int representing the coordinates to start placing the backdrop nodes
    """
    write_nodes: dict[Path, list[nuke.Node]] = {}  # type: ignore
    offset = (100, 200)

    for sequence in sequences:
        path = sequence.get_path().parent
        wrapper = ReadWrapper.from_image_file(sequence)
        node = wrapper.read_node
        if path not in write_nodes.keys():
            write_nodes[path] = []
        write_nodes[path].append(node)

    try:
        first_node = list(write_nodes.values())[0][0]
    except Exception as e:
        print(f"no write nodes were created: {e}")
        # return

    if origin is None:
        origin = first_node["xpos"].getValue(), first_node["ypos"].getValue()
    else:
        origin = origin[0], origin[1] + offset[1]

    xcount = 0
    ycount = 0
    # count = count or 0

    for path, nodes in write_nodes.items():
        for node in nodes:
            node["xpos"].setValue(origin[0] + xcount * offset[0])
            node["ypos"].setValue(origin[1] + ycount * offset[1])
            xcount += 1
        backdrop(nodes, path.as_posix(), count)
        xcount = 0
        ycount += 1
        count += 1

    return (origin[0], origin[1] + (ycount - 1) * offset[1]), count


def resize_backdrop_to_fit_label(backdrop_node):
    """
    Resizes a backdrop to fit its label text content
    Args:
        backdrop_node: The backdrop node to resize
    """

    label = backdrop_node["label"].value()

    temp_text = nuke.Text_Knob("temp_text", "")  # type: ignore
    temp_text.setLabel(label)

    font_width_approx = 7  # Average width of a character in pixels

    lines = label.split("\n")
    max_chars = max([len(line) for line in lines])

    text_width = max_chars * font_width_approx

    padding_x = 20

    new_value = text_width * 2 + 2 * padding_x
    if new_value < backdrop_node["bdwidth"].getValue():
        return

    backdrop_node["bdwidth"].setValue(text_width * 2 + 2 * padding_x)
