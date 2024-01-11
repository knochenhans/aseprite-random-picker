# Aseprite Picker

Picks random layers from layer groups of an Aseprite file and saves a final png image. For example can be used to generate faces from a set of elements.

## Usage

This script picks random layers from predefined layer groups in an Aseprite file and generates a final image. 

You can run the script with the following command:

```bash
python aseprite-random-picker.py input_file -o output -c config -n count
```

Where:

* input_file: Path to the input Aseprite file.
* -o, --output: File name of the output image (default: output_image.png). Count number will be added.
* -c, --config: Path to the config file (default: facebuilder.json).
* -n, --count: How many images to generate (default: 5).

### Example

Here's an example of how to use the script:

```bash
python aseprite-random-picker.py "face.ase" -o "random_face.png" -c "facebuilder.json" -n 50
```

In this example, the script will take the Aseprite file face.ase, pick random layers based on the configuration in facebuilder.json, generate 50 images, and save the final images as `random_face_1.png`, `random_face_2.png`, etc.

### Config File

The config file in JSON format consists of group layer names Aseprite Picker will look for in the Aseprite file to randomly choose layers from, accompanied by weights. Layer groups with a weight of `100` will always be added to output image:

```[["Face"], [100]]```

If you want to randomly ignore a specific config entry (that is, a set of layer groups), you can add an empty group name and the respective weight, like so:

```[["Hair", "Hat", ""], [70, 50, 80]]```

Thus, the script will randomly choose the layer name `Hair`, `Hat`, or will ignore this config entry entirely.

An example config (`facebuilder.json`) is provided.

## Requirements

* install https://github.com/Eiyeron/py_aseprite, for example via `pip install --upgrade https://github.com/Eiyeron/py_aseprite/tarball/master`

## Limits and Ideas

This script is somewhat quick and dirty for now, it only works based on the first frame found in the Aseprite file and uses it’s palette (yes, it works only with files with index colors for now, I’ve been to lazy to implement this for RGB images).

A future improvement could be to also apply randomization weights to the layers itself (not just layer groups), maybe by extracting numbers from layer names or so.

## License

This project is licensed under the [MIT License](LICENSE).