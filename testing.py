from main import Visualize, Animation, GifTranslator
from utils import generate_points


#points = "coords_2021.csv"
points = generate_points(2000, tree=False)

gif = GifTranslator('examples/rickroll_7s.gif', points, 'y', 'z')

anim = Animation(points, gif.get_RGB, gif.frames)
colors = anim.run()

vis = Visualize(points, colors, framerate=30)
vis.run()