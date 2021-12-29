import argparse
from main import Animation, GifTranslator

if __name__ == "__main__":
    """
    Pareses arguments and runs animation.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("coords", help="The path to the coordinates csv")
    parser.add_argument("gif", help="The path to the gif file")
    parser.add_argument("-o", "--output", default="export.csv", help="Name of the output csv file")
    parser.add_argument("--width", default="y", choices=['x', 'y', 'z'], help="Dimension corresponding to the width of the gif.")
    parser.add_argument("--height", default="z", choices=['x', 'y', 'z'], help="Dimension corresponding to the height of the gif.")
    parser.add_argument("--disable_aspect", action='store_true', help="Do not maintain the aspect ratio of the gif, and instead fit it exactly to the given coordinates.")
    args = parser.parse_args()

    maintain_aspect = not args.disable_aspect
    gif = GifTranslator(args.gif, args.coords, args.width, args.height, maintain_aspect=maintain_aspect)
    anim = Animation(args.coords, gif.get_RGB, gif.frames)
    anim.run()
    anim.export(args.output)
