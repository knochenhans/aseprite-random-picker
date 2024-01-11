import argparse
import datetime
import json
import os
import random

from aseprite import AsepriteFile, CelChunk, LayerGroupChunk
from PIL import Image


def find_child(parsed_file, layer_group_index, layer_index) -> CelChunk | None:
    for chunk in parsed_file.frames[0].chunks:
        if isinstance(chunk, CelChunk):
            if chunk.layer_index == layer_group_index + layer_index:
                return chunk
    return None


def write_with_palette(palette_dict: dict, child: CelChunk):
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
            pixel_dict = palette_dict[data[y][x]]
            pixel = (
                pixel_dict["red"],
                pixel_dict["green"],
                pixel_dict["blue"],
                pixel_dict["alpha"],
            )
            if data[y][x] != 0:
                image.putpixel((x, y), pixel)
    return image


class Element:
    def __init__(
        self, name: str, index: int, weight: float, chunk: CelChunk | None = None
    ):
        self.name: str = name
        self.index: int = index
        self.weight: float = weight
        self.chunk: CelChunk | None = chunk


class Group:
    def __init__(self, name: str, elements: list):
        self.name: str = name
        self.elements: list = elements

    def get_random_element(self):
        return random.choices(self.elements, weights=[e.weight for e in self.elements])[
            0
        ]


def get_groups_and_chunks(parsed_file) -> list:
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


# Preset groups from optional elements and alternative elements
def choose_basic_groups(element_groups: list) -> list:
    choices = []

    for group in element_groups:
        element_names = group[0]
        element_weights = group[1]

        choice = random.choices(element_names, weights=element_weights)[0]

        if choice == "":
            continue

        choices.append(choice)
    return choices


# Generate face by choosing final elements from each chosen group
def generate_face(groups, palette_dict, chosen_groups, final_width=64, final_height=64):
    final_image = Image.new("RGBA", (final_width, final_height))

    for group in groups:
        if group.name in chosen_groups:
            chosen_element = group.get_random_element()

            image = write_with_palette(palette_dict, chosen_element.chunk)

            final_image.paste(
                image, (chosen_element.chunk.x_pos, chosen_element.chunk.y_pos), image
            )

    return final_image


def main(
    input_file_path: str, output_file_path: str, config_file_path: str, count: int
):
    with open(input_file_path, "rb") as f:
        parsed_file = AsepriteFile(f.read())

        # Get palette from first frame, assuming all frames have the same palette
        first_frame_chunk = parsed_file.frames[0].chunks[0]
        palette_dict: dict = first_frame_chunk.colors

        groups = get_groups_and_chunks(parsed_file)

        final_width, final_height = parsed_file.header.width, parsed_file.header.height

        with open(config_file_path, "r") as file:
            element_groups = json.load(file)


        for i in range(count):
            basic_elements = choose_basic_groups(element_groups)
            face = generate_face(
                groups, palette_dict, basic_elements, final_width, final_height
            )

            current_datetime = datetime.datetime.now()
            # formatted_datetime = current_datetime.strftime("%Y%m%d_%H%M%S")

            file_name, output_extension = os.path.splitext(output_file_path)

            # filename = f"{file_name}_{formatted_datetime}-{i}{output_extension}"
            filename = f"{file_name}_{i}{output_extension}"

            face.save(filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pick random layers from predefined layer groups in an Aseprite file and generate a final image."
    )

    parser.add_argument("input_file", type=str, help="Path to the input Aseprite file")
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="output_image.png",
        help="Path to the output image file (default: output_image.png)",
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default="facebuilder.json",
        help="Path to the config file (default: facebuilder.json)",
    )
    parser.add_argument(
        "--count",
        "-n",
        type=int,
        default=5,
        help="How many images to generate (default: 5)",
    )

    args = parser.parse_args()

    input_file_path = args.input_file
    output_file_path = args.output
    config_file_path = args.config
    main(input_file_path, output_file_path, config_file_path, args.count)
