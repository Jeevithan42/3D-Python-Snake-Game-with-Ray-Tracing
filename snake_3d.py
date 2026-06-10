import sys
# Ensure Panda3D is installed in your Python environment before running.
# If missing, run: pip install panda3d
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, Point3, DirectionalLight, AmbientLight, LVector3, NodePath, TextNode, TransparencyAttrib, ClockObject
# simplepbr import skipped – default Panda3D lighting is used

from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
import random

# Game configuration
WIDTH, HEIGHT = 800, 800          # Window size (pixels)
BLOCK_SIZE = 20                     # Size of each grid cell (world units)
GRID_W = WIDTH // BLOCK_SIZE
GRID_H = HEIGHT // BLOCK_SIZE
FPS_BASE = 12

# Colors (RGB, 0-1 range)
WHITE = (1, 1, 1, 1)
GREEN = (0, 0.9, 0, 1)
DARK_GREEN = (0, 0.6, 0, 1)
RED = (0.9, 0.1, 0.1, 1)
GREY = (0.5, 0.5, 0.5, 0.5)

class Snake3D(ShowBase):
    def __init__(self):
        super().__init__()
        print("Snake3D initialized – window opened")
        self.disableMouse()  # we'll control camera manually
        self.camera.setPos(GRID_W/2, -30, GRID_H/2)
        self.camera.lookAt(GRID_W/2, 0, GRID_H/2)
        self.accept('escape', sys.exit)  # allow quick exit
        self.setup_lights()
        # Ray tracing (RTX) support requires the RenderPipeline addon. Install with:
# pip install panda3d-renderpipeline
# Then enable with the following (uncomment after installation):
# from panda3d.core import loadPrcFileData
# loadPrcFileData('', 'load-display pipgui')  # example to use pip GUI for pipeline
# base.enableRenderPipeline()

        # Game state
        self.snake = [(GRID_W//2, GRID_H//2)]   # list of (x, y) grid cells
        self.direction = (0, 0)               # dx, dy in grid units
        self.food = self.spawn_food()
        self.score = 0
        self.level = 1
        self.current_mode = "Classic Mode"
        self.game_over = False
        self.fps = FPS_BASE

        # Rendering containers
        self.snake_node = self.render.attachNewNode('snake')
        self.food_node = self.render.attachNewNode('food')
        self.ui = {}
        self.create_ui()
        # Preload models for reuse (avoid loading each frame)
        # Set a visible background color for debugging
        self.setBackgroundColor(0.2, 0.2, 0.4)

        # Load prototypes safely – fallback to simple cube if missing
        try:
            self._cube_proto = self.loader.loadModel('models/misc/rgbCube')
        except Exception as e:
            print('Failed to load rgbCube model:', e)
            self._cube_proto = self.loader.loadModel('models/box')  # fallback generic cube
        try:
            self._sphere_proto = self.loader.loadModel('models/misc/sphere')
        except Exception as e:
            print('Failed to load sphere model:', e)
            self._sphere_proto = self.loader.loadModel('models/sphere')  # fallback generic sphere
        self.build_scene()

        # Input handling
        self.accept('arrow_up', self.set_direction, [(0, 1)])
        self.accept('arrow_down', self.set_direction, [(0, -1)])
        self.accept('arrow_left', self.set_direction, [(-1, 0)])
        self.accept('arrow_right', self.set_direction, [(1, 0)])
        self.accept('w', self.set_direction, [(0, 1)])
        self.accept('s', self.set_direction, [(0, -1)])
        self.accept('a', self.set_direction, [(-1, 0)])
        self.accept('d', self.set_direction, [(1, 0)])

        # Game loop task
        self.taskMgr.add(self.update, "gameLoop")


    def setup_lights(self):
        # Simple directional light to simulate a sun
        dlight = DirectionalLight('dlight')
        dlight.setColor((0.8, 0.8, 0.8, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(45, -45, 0)
        self.render.setLight(dlnp)
        # Ambient light for soft shadows
        alight = AmbientLight('alight')
        alight.setColor((0.2, 0.2, 0.2, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)

    def create_ui(self):
        # On‑screen text for score/level
        self.ui['score'] = OnscreenText(text='Score: 0', pos=(-1.3, 0.9), scale=0.07,
                                        fg=(1,1,1,1), align=TextNode.ALeft)
        self.ui['level'] = OnscreenText(text='Level: 1', pos=(-1.3, 0.8), scale=0.07,
                                        fg=(1,1,1,1), align=TextNode.ALeft)
        self.ui['mode'] = OnscreenText(text='Mode: Classic', pos=(-1.3,0.7), scale=0.07,
                                        fg=(1,1,1,1), align=TextNode.ALeft)

    def build_scene(self):
        # Clear previous geometry
        self.snake_node.node().removeAllChildren()
        self.food_node.node().removeAllChildren()
        # Build snake cubes using preloaded prototype
        for i, (x, y) in enumerate(self.snake):
            cube = self._cube_proto.copyTo(self.snake_node)
            cube.setScale(BLOCK_SIZE/2)
            cube.setPos(x * BLOCK_SIZE + BLOCK_SIZE/2,
                        0,
                        y * BLOCK_SIZE + BLOCK_SIZE/2)
            col = GREEN if i == 0 else DARK_GREEN
            cube.setColor(col)
        # Food sphere using prototype
        sphere = self._sphere_proto.copyTo(self.food_node)
        sphere.setScale(BLOCK_SIZE/2)
        fx, fy = self.food
        sphere.setPos(fx * BLOCK_SIZE + BLOCK_SIZE/2, 0, fy * BLOCK_SIZE + BLOCK_SIZE/2)
        sphere.setColor(RED)

    def set_direction(self, dir_vec):
        if self.game_over:
            return
        # Prevent reversing directly
        if (dir_vec[0] == -self.direction[0] and dir_vec[0] != 0) or \
           (dir_vec[1] == -self.direction[1] and dir_vec[1] != 0):
            return
        self.direction = dir_vec

    def spawn_food(self):
        while True:
            x = random.randint(0, GRID_W-1)
            y = random.randint(0, GRID_H-1)
            if (x, y) not in self.snake:
                return (x, y)

    def update(self, task):
        
        if self.game_over:
            return Task.done
        dt = ClockObject.getGlobalClock().getDt()  # use ClockObject for delta time
        # Simple frame‑rate independent timer – move the snake every X seconds
        if not hasattr(self, 'move_timer'):
            self.move_timer = 0.0
        self.move_timer += dt
        move_interval = 1.0 / self.fps
        if self.move_timer >= move_interval:
            self.move_timer -= move_interval
            self.step()
        return Task.cont

    def step(self):
        if self.direction == (0, 0):
            return  # not moving yet
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        # Border handling – classic mode stops game
        if not (0 <= new_head[0] < GRID_W and 0 <= new_head[1] < GRID_H):
            self.end_game()
            return
        # Self‑collision
        if new_head in self.snake:
            self.end_game()
            return
        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 10
            if self.score % 50 == 0:
                self.level += 1
                self.fps = FPS_BASE + (self.level - 1) * 2
            self.food = self.spawn_food()
        else:
            self.snake.pop()
        # Update UI
        self.ui['score'].setText(f"Score: {self.score}")
        self.ui['level'].setText(f"Level: {self.level}")
        self.build_scene()

    def end_game(self):
        self.game_over = True
        # Store the game‑over text node so we can clean it up later
        self.game_over_msg = OnscreenText(text='Game Over – Press R to Restart', pos=(0,0), scale=0.1,
                                          fg=(1,0,0,1), mayChange=False)
        self.accept('r', self.restart)

    def restart(self):
        # Ensure UI exists (re‑create if missing)
        self.ui = {}
        self.create_ui()
        # Ensure rendering containers exist (re‑create after a full reset)
        if not hasattr(self, 'snake_node'):
            self.snake_node = self.render.attachNewNode('snake')
        if not hasattr(self, 'food_node'):
            self.food_node = self.render.attachNewNode('food')
        # Ensure prototype models are loaded (needed after a restart)
        if not hasattr(self, '_cube_proto'):
            self._cube_proto = self.loader.loadModel('models/misc/rgbCube')
        if not hasattr(self, '_sphere_proto'):
            self._sphere_proto = self.loader.loadModel('models/misc/sphere')
        self.snake = [(GRID_W//2, GRID_H//2)]
        self.direction = (0,0)
        self.food = self.spawn_food()
        self.score = 0
        self.level = 1
        self.fps = FPS_BASE
        self.game_over = False
        # Update UI safely
        self.ui['score'].setText('Score: 0')
        self.ui['level'].setText('Level: 1')
        self.build_scene()
        # Clean up any leftover game‑over messages
        if hasattr(self, 'game_over_msg'):
            self.game_over_msg.removeNode()
            del self.game_over_msg
        # Re‑attach the loop task
        if not self.taskMgr.hasTaskNamed('gameLoop'):
            self.taskMgr.add(self.update, 'gameLoop')

if __name__ == '__main__':
    app = Snake3D()
    app.run()
