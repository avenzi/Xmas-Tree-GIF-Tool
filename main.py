import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image, ImageSequence


def load_csv(filename):
    return np.loadtxt(filename, delimiter=',', encoding='utf-8-sig')


def loading(msg, num, max_num=None):
    if max_num is None:
        print(f"\r{msg} {num}", end=' '*10)
    else:
        print(f"\r{msg} {num} / {max_num}", end=' '*10)


class GifTranslator:
    def __init__(self, filename, points, width_direction, height_direction, maintain_aspect=True, flip_vertical=False, flip_horizontal=False, verbose=True):
        """
        <filename> filepath of the GIF
        <width_direction> which direction the width of the GIF should be in. 'x', 'y', or 'z'
        <height_direction> which direction the height of the GIF should be in. 'x', 'y', or 'z'
        <maintain_aspect> Whether to maintain the aspect ratio of the gif.
        <flip_vertical> Whether to flip the animation vertically.
        <flip_horizontal> Whether to flip the animation horizontally.
        <verbose> Whether to print status output.
        """
        if (type(points) == str):  # csv file name
            points = load_csv(points)

        self.flip_vertical = flip_vertical
        self.flip_horizontal = flip_horizontal
        self.maintain_aspect = maintain_aspect

        directions = {'x':0, 'y':1, 'z':2}  # number is the index into the args passed into get_RGB
        assert width_direction in directions and height_direction in directions, "Height and Width must be 'x', 'y', or 'z'"
        self.width = directions[width_direction]  # width dimension
        self.height = directions[height_direction]  # height dimension

        self.points_width = (np.min(points[:, self.width]), np.max(points[:, self.width]))
        self.points_height = (np.min(points[:, self.height]), np.max(points[:, self.height]))

        gif = Image.open(filename)
        images = []
        i = 0
        for frame in ImageSequence.Iterator(gif):
            data = frame.copy().convert('RGB').getdata()
            arr = np.array(data, dtype=np.uint8)
            arr = arr.reshape(frame.size[1], frame.size[0], 3)
            if not self.flip_vertical:  # the above code produces vertically flipped gifs for some reason.
                arr = np.flip(arr, axis=0)
            if self.flip_horizontal:
                arr = np.flip(arr, axis=1)
            images.append(arr)
            i += 1
            if verbose:
                loading('Loading Frames:', i)

        self.gif = np.array(images)
        self.frames = self.gif.shape[0]
        self.gif_height = self.gif.shape[1]  # actual height and width of the gif array
        self.gif_width = self.gif.shape[2]

        # get aspect ratio (h/w) of the coordinate space
        ratio = (self.points_height[1]-self.points_height[0]) / (self.points_width[1]-self.points_width[0])

        if verbose:
            print()
            print('coords height:', self.points_height)
            print('coords width:', self.points_width)
            print('coords aspect ratio:', ratio)
            print('gif height:', self.gif_height)
            print('gif width:', self.gif_width)

        # if aspect is to be maintained, set min and max height/width to map into the coordinates
        if self.maintain_aspect:
            mid_height = int(self.gif_height / 2)
            mid_width = int(self.gif_width / 2)
            if self.gif_height <= self.gif_width:  # shorter height
                scale = int(mid_height / ratio)  # get how much to scale the width by
                self.idx_height = (0, self.gif_height-1)  # full height
                self.idx_width = (mid_width-scale, mid_width+scale)
            else:  # shorter width
                scale = int(mid_width * ratio)  # get how much to scale the height by
                self.idx_width = (0, self.gif_width-1)  # full width
                self.idx_height = (mid_height-scale, mid_height+scale)

        else:  # otherwise fit to the whole range of height/width indexes
            self.idx_height = (0, self.gif_height-1)
            self.idx_width = (0, self.gif_width-1)

        if verbose:
            print("gif window height:", self.idx_height)
            print('gif window width:', self.idx_width)

    def convert(self, val, inputs, outputs):
        """
        Convert a point from the input space to the output space. It's just a linear mapping.
        val: the value to convert
        inputs: Tuple of the min and max input value
        outputs: Tuple of the min and max output value
        """
        return int(((val-inputs[0]) * ((outputs[1]-outputs[0]) / (inputs[1]-inputs[0]))) + outputs[0])

    def get_RGB(self, *args):
        """
        Convert a 3D point and time into an RGB value from the GIF.
        Intended to be passed into an Animation object's func parameter.
        """
        # get x, y, or z depending on the height and width dimensions
        width = args[self.width]
        height = args[self.height]

        # convert from coordinates into width/height index in gif
        width_idx = self.convert(width, self.points_width, self.idx_width)
        height_idx = self.convert(height, self.points_height, self.idx_height)

        # if height/width index is within the gif array
        if 0 <= width_idx < self.gif_width and 0 <= height_idx < self.gif_height:
            # get RGB of this pixel in this frame. args[3] is 't', the frame time index
            R, G, B = self.gif[args[3], height_idx, width_idx, :]
        else:  # otherwise, return black. This happens only if self.maintain_aspect is True
            R, G, B = 0, 0, 0

        return R, G, B


class Animation:
    def __init__(self, points, func, frames, normalize=True, verbose=True):
        """
        <points> a numpy array of coordinates OR a filepath to cordinates in CSV format
        <func> a function that takes in x, y, z, and t and returns R, G, B
        <frames> the number of frames
        <normalize> whether to normalize the RGB values returned from func to between 0 and 1
            (this will happen regardless if the max value generated is > 1, but not if it's lower)
        <verbose> Whether to print status output.
        """
        if (type(points) == str):  # csv file name
            points = load_csv(points)
        self.points = points
        self.func = func
        self.frames = frames
        self.colors = np.empty((self.frames, len(self.points), 3))  # array to be given to Visualize
        self.normalize = normalize
        self.verbose = verbose

    def run(self):
        frames = []
        for t in range(self.frames):
            frame = []  # array of RGB arrays
            for x, y, z in self.points:
                RGB = self.func(x, y, z, t)
                frame.append(np.array(RGB))
            frame = np.stack(frame, axis=0)
            frames.append(frame)

            if self.verbose:
                loading('Calculating Frame:', t+1, self.frames)

        self.colors = np.stack(frames, axis=0)
        min_color = self.colors.min(axis=None)
        if min_color < 0 or self.normalize:
            self.colors = self.colors - min_color

        max_color = self.colors.max(axis=None)
        if max_color != 0 and (max_color > 1 or self.normalize):
            self.colors = self.colors / max_color

        return self.colors

    def export(self, filename):
        """ Export animation to CSV """
        frames = []
        i = 0
        for frame in self.colors:
            frame = frame.flatten()*255  # convert to 255 RGB
            frame = np.insert(frame, 0, i)  # add frame number
            frames.append(frame)
            i += 1
        export_array = np.array(frames)

        # generate header
        header = ['FRAME_ID']
        for i in range(len(self.points)):
            header.append(f"R_{i}")
            header.append(f"G_{i}")
            header.append(f"B_{i}")
        header = ','.join(header)

        np.savetxt(filename, export_array, delimiter=",", fmt='%3d', header=header, comments='')


class Visualize:
    def __init__(self, points, animation, framerate=30, verbose=True):
        """
        Visualize a given CSV animation in GIFT format accoridng to the given coordinates.
        <points> a filepath to cordinates in CSV format OR a 2D numpy array
        <animation> a filepath to a file in GIFT CSV format OR a 4D numoy array (format described in import_aniamtion())
        <framerate> playback framerate in FPS
        <verbose> Whether to print status output.
        """
        self.points = None  # coords
        self.colors = None  # animation
        self.num_frames = 0
        self.num_points = 0

        self.import_points(points)
        self.import_animation(animation)
        assert self.points is not None, "Data points not given."
        assert self.colors is not None, "Color animation sequence not given."
        assert len(self.points) == len(self.colors[0]), f"Data points and first color frame are not the same length. Points: {len(self.points)}, Colors[0]: {len(self.colors[0])}"

        self.verbose = verbose
        self.interval = 1000/framerate  # from FPS to interval between frames in ms

        self.fig = None
        self.ax = None
        self.scat = None  # scatter object to be updated
        self.setup()

    def run(self):
        """ Run the animation """

        x, y, z = self.points.T  # get arrays of all x, y, and z coords
        colors = self.colors[0]  # get first frame of colors for each point

        self.scat = self.ax.scatter(x, y, z, c=colors, s=10)

        # Animation function
        self.anim = animation.FuncAnimation(
            self.fig, self.update, self.num_frames, interval=self.interval, blit=False
        )
        plt.show()

    def save(self, filename):
        """ Save animation as mp4 """
        self.anim.save(filename)

    def import_points(self, points):
        """
        If numpy array:
            Points must be a 2D array: an array of points in 3D space.

        If CSV filename:
            Rows are each point and columns are the X, Y, and Z coords.
        """
        if (type(points) == str):  # csv file name
            self.points = load_csv(points)
        else:  # numpy array
            self.points = points
        self.num_points = len(self.points)

    def import_animation(self, colors):
        """
         If numpy array:
            Points must be a 3D array: an array of arrays of RGB values.
            Axis 0: each frame in the animation
            Axis 1: Each point in the dataset
            Axis 2: RGB values between 0 and 1

        If CSV filename:
            Import colors from a CSV file in GIFT format (RGB values between 0 and 255
        """
        frames = []
        if (type(colors) == str):
            gift = np.loadtxt(colors, delimiter=',', skiprows=1, encoding='utf-8-sig')
            for i in range(len(gift)):  # for each row
                rgb = gift[i][1:]  # get row of colors and ignore index (first column)
                assert len(rgb) % 3 == 0, f"A row in the animation file is not a multiple of 3. Row #{i}"
                rgb = rgb/255  # normalize between 0 and 1
                rgb = rgb.reshape((self.num_points, 3))
                frames.append(rgb)
            colors = np.array(frames)

        # append alpha value of 1 to each RGB array (necessary to set 3D scatter colors
        shape = (colors.shape[0], colors.shape[1], 1)  # get shape for array of 1s
        colors = np.append(colors, np.ones(shape), axis=2)
        self.colors = colors
        self.num_frames = len(colors)

    def setup(self):
        """ Creates the figure and axes """
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(projection='3d')

        min_coords = self.points.min(axis=0)
        max_coords = self.points.max(axis=0)
        widths = max_coords - min_coords  # width of each axis

        self.ax.set_box_aspect(widths)  # set 3D aspect ratio so tree isn't squished
        self.ax.set_axis_off()  # turn off axes
        self.ax.set_facecolor((0.05, 0.05, 0.05))  # set backgorund to something dark

        #self.ax.set_xlabel('X')
        #self.ax.set_ylabel('Y')
        #self.ax.set_zlabel('Z')

        self.ax.view_init(0, 0)  # start head-on along the X axis

    def update(self, frame_num):
        """ Called for each frame of the animation """
        # Print frame info if verbose
        if self.verbose:
            loading('Displaying:', frame_num+1, self.num_frames)

        frame_colors = self.colors[frame_num]  # get this frame's colors
        self.scat.set_color(frame_colors)
        return self.scat,
