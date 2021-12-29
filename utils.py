import numpy as np

def generate_points(num, tree=False):
    """ Generates <num> random points to use for testing """
    x_ext = (-1, 1)
    y_ext = (-1, 1)
    z_ext = (0, 3)

    x_arr = np.random.uniform(x_ext[0], x_ext[1], num)
    y_arr = np.random.uniform(y_ext[0], y_ext[1], num)
    z_arr = np.random.uniform(z_ext[0], z_ext[1], num)
    points = np.array((x_arr, y_arr, z_arr)).T

    if tree:  # limit them to a tree shape
        cone_points = []
        for point in points:
            x, y, z = point
            if (z - 3) ** 2 >= 10 * (x ** 2 + y ** 2) and z >= z_ext[0] and z <= z_ext[1]:
                cone_points.append(point)
        points = np.stack(cone_points, axis=0)

    return points