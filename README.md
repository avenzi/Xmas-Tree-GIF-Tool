This repo is made to participate in [Matt Parker's XmasTree 2021](https://github.com/standupmaths/xmastree2021) event.

Convert any given animated gif file into an animation in GIFT CSV format.

#### Convert a Gif:
- First, run `pip3 install -r requirements.txt` to install the necessary packages.  
- To convert a gif you will need a CSV file with coordinates of the Xmas tree's LED lights; Matt Parker's 2021 coordinates are given in `examples/coords_2021.csv`.  
- Run this command:  `python3 convert.py <path_to_coords.csv> <path_to_gif.gif>`
- The output will be a CSV file in GIFT format which animates the given gif file according to the given LED coordinates.  
- In order to see the gif as clearly as possible, you need to look directly at the tree head-on from the positive X direction (as was discussed [here](https://github.com/standupmaths/xmastree2021/issues/21#issuecomment-1002297485)).
- This conversion also assumes that one frame in the gif corresponds to one frame in the output with no timing information.

Some optional parameters for convert.py:
- -h, --help:  display these options and exit.
- -o, --output <filename.csv>: Name of the output file. By default, the output file will be named `export.csv`.
- --width <x, y, or z>: Dimension along which the width of the gif will be rendered. This is `y` by default.
- --height <x, y, or x>: Dimension along which the height of the gif will be rendered. This is `z` by default.
- --disable_aspect: Do not maintain the aspect ratio of the gif, and instead fit it exactly to the boundaries of the given coordinates.


#### Previewing a CSV file
This repo also provides the ability to preview a GIFT CSV file.
- pip install requirements if not already
- run: `python3 animate.py <path_to_coords.csv> <path_to_animation.csv>`
- The result *should* be matplotlib's animated 3D dialog box running the animation.

Optional parameters for animate.py:
- -h, --help: display these options and exit.
- -f, --framerate <integer>: Define the framerate (in FPS) at which to playback the animation. Default is 30. Note that will large coordinate datasets, the framerate may be capped by what matplotlib can handle.


#### Examples
Provided in the `examples` directory are some gifs and their corresponding GIFT CSV files (generated with `coords_2021.csv`), which may be previewed as described above.
- bad_apple_full.gif: obviously
- bad_apple_14s.gif: just the first 14 seconds
- amogus.gif: a🅱ogus
- rickroll_7s.gif: rickroll intro
- circle.gif: just a static red circle. Good for finding the right angle from which to look at the tree.