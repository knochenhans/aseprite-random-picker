import random

from aseprite import AsepriteFile, CelChunk, LayerGroupChunk
from PIL import Image


class Element:
    """Element of a group with name, index, weight and CelChunk from Aseprite file"""
    def __init__(
        self, name: str, index: int, weight: float, chunk: CelChunk | None = None
    ):
        self.name: str = name
        self.index: int = index
        self.weight: float = weight
        self.chunk: CelChunk | None = chunk


class Group:
    """Group of elements with name and list of elements"""
    def __init__(self, name: str, elements: list):
        self.name: str = name
        self.elements: list = elements

    def get_random_element(self):
        return random.choices(self.elements, weights=[e.weight for e in self.elements])[
            0
        ]


def find_child(parsed_file, layer_group_index, layer_index) -> CelChunk | None:
    """Find and return child CelChunk from parsed Aseprite file"""
    for chunk in parsed_file.frames[0].chunks:
        if isinstance(chunk, CelChunk):
            if chunk.layer_index == layer_group_index + layer_index:
                return chunk
    return None


def cel_to_image(palette: dict, child: CelChunk):
    """Convert Aseprite CelChunk to PIL Image"""
    data_raw = child.data["data"]
    child_width: int = child.data["width"]
    child_height: int = child.data["height"]
    array_1D = [i for i in data_raw]
    data = [
        array_1D[i * child_width : (i + 1) * child_width] for i in range(child_height)
    ]

    image = Image.new("RGBA", (child_width, child_height))

    for y in range(child_height):
        for x in range(child_width):
            pixel_dict = palette[data[y][x]]
            pixel = (
                pixel_dict["red"],
                pixel_dict["green"],
                pixel_dict["blue"],
                pixel_dict["alpha"],
            )
            if data[y][x] != 0:
                image.putpixel((x, y), pixel)
    return image


def get_groups(parsed_file) -> list:
    """Get groups from parsed Aseprite file"""
    groups: list = []
    group_count = 0
    for chunk in parsed_file.frames[0].chunks:
        if isinstance(chunk, LayerGroupChunk):
            group_count += 1

            elements: list = []

            for child in chunk.children:
                child_idx = child.layer_index

                child_chunk = find_child(parsed_file, group_count, child_idx)

                if child is None:
                    print(
                        f"Child is None for group {chunk.name} with index {child_idx}"
                    )
                    break

                if child_chunk is None:
                    break
                elements.append(Element(child.name, child_idx, 1, child_chunk))
            groups.append(Group(chunk.name, elements))
    return groups


def choose_basic_groups(element_groups: list) -> list:
    """Choose groups from optional elements and alternative elements"""
    choices = []

    for group in element_groups:
        element_names = group[0]
        element_weights = group[1]

        choice = random.choices(element_names, weights=element_weights)[0]

        if choice == "":
            continue

        choices.append(choice)
    return choices
