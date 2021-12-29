import argparse
from main import Visualize

if __name__ == "__main__":
    """ Pareses arguments and runs animation """
    parser = argparse.ArgumentParser()
    parser.add_argument("coords", help="The path to the coordinates csv")
    parser.add_argument("animation", help="The path to the animation csv")
    parser.add_argument("-f", '--framerate', default=30, type=int, help="The animation frame rate")
    args = parser.parse_args()

    vis = Visualize(args.coords, args.animation, framerate=args.framerate)
    vis.run()