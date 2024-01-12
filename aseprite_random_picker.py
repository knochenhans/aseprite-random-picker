import argparse
import datetime
import json
import os
import random

from aseprite import AsepriteFile
from PIL import Image

from aseprite_library import (
    get_groups,
    cel_to_image,
    choose_basic_groups,
)


def generate_merged_image(groups, palette_dict, chosen_groups, final_width=64, final_height=64):
    """Generate merged image by choosing final elements from each chosen group"""
    final_image = Image.new("RGBA", (final_width, final_height))

    for group in groups:
        if group.name in chosen_groups:
            chosen_element = group.get_random_element()

            image = cel_to_image(palette_dict, chosen_element.chunk)

            final_image.paste(
                image, (chosen_element.chunk.x_pos, chosen_element.chunk.y_pos), image
            )

    return final_image


def create_image_grid(images, cols):
    """Create a grid of images"""
    rows = (len(images) + cols - 1) // cols

    w, h = images[0].size
    grid = Image.new("RGBA", size=(cols * w, rows * h), color="white")
    empty_image = Image.new("RGBA", (w, h), color="white")

    for i, img in enumerate(images):
        grid.paste(img, box=(i % cols * w, i // cols * h), mask=img)

    for i in range(len(images), rows * cols):
        grid.paste(empty_image, box=(i % cols * w, i // cols * h))

    return grid


def get_palette(parsed_file) -> dict:
    """Get palette from first frame, assuming all frames have the same palette"""
    first_frame_chunk = parsed_file.frames[0].chunks[0]
    return first_frame_chunk.colors


def main(
    input_file_path: str,
    output_file_path: str,
    config_file_path: str,
    count: int,
    grid: bool = False,
):
    with open(config_file_path, "r") as file:
        element_groups = json.load(file)

    with open(input_file_path, "rb") as f:
        parsed_file = AsepriteFile(f.read())

    if parsed_file is not None and len(element_groups) > 0:
        groups = get_groups(parsed_file)

        palette = get_palette(parsed_file)

        final_width, final_height = parsed_file.header.width, parsed_file.header.height

        face_images = []

        for i in range(count):
            basic_elements = choose_basic_groups(element_groups)
            face_images.append(
                generate_merged_image(
                    groups, palette, basic_elements, final_width, final_height
                )
            )

        if grid:
            image_grid = create_image_grid(face_images, 5)
            image_grid.convert("RGB").resize(
                (image_grid.width * 2, image_grid.height * 2)
            ).save(output_file_path)
        else:
            for i in range(len(face_images)):
                face = face_images[i]
                # current_datetime = datetime.datetime.now()
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
    parser.add_argument(
        "--grid",
        "-g",
        type=int,
        metavar="COL_WIDTH",
        help="Create an image grid with the generated images. Specify the column width.",
    )

    args = parser.parse_args()

    input_file_path = args.input_file
    output_file_path = args.output
    config_file_path = args.config
    main(input_file_path, output_file_path, config_file_path, args.count, args.grid)
