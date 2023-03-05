import math
import random
import goodgame as gg
import scene
import main
try:
    import cymunk as cp
    is_pymunk = False
except ImportError:
    import pymunk as cp
    is_pymunk = True


sqrt_2 = math.sqrt(2)


class Circle:
    def __init__(self, pos: any) -> None:
        self.color = (random.uniform(0, 255), random.uniform(0, 255), random.uniform(0, 255))
        self.radius = random.uniform(5, 75)
        self.img_size = self.radius * sqrt_2
        self.img_offset = self.img_size / 2
        self.mass = random.uniform(0.2, 1.5)
        self.moment = cp.moment_for_circle(self.mass, 0, self.radius)
        self.body = cp.Body(self.mass, self.moment)
        self.body.position = pos
        self.shape = cp.Circle(self.body, self.radius)
        self.shape.elasticity = random.uniform(0, 1.1)
        self.shape.friction = random.uniform(0, 2)


class Scene(scene.Scene):
    def __init__(self, renderer: main.Renderer, data: any) -> None:
        super().__init__(renderer, data)
        self.destroyed = True
        self.a: main.App = renderer.app
        self.w: main.Window = renderer.window
        self.r: main.Renderer = renderer
        self.fps_font: gg.TTF = data[0]
        self.image = self.r.texture_from_surface(data[1])
        self.size = self.r.get_output_size()
        if is_pymunk:
            self.space = cp.Space(threaded=True)
        else:
            self.space = cp.Space()
        self.space.gravity = 0, 1000
        self.floor_rect = (20, self.size[1] - 30, self.size[0] - 40, 20)
        self.floor = cp.Segment(
            self.space.static_body,
            (self.floor_rect[0], self.floor_rect[1] + self.floor_rect[3] / 2),
            (self.floor_rect[0] + self.floor_rect[2], self.floor_rect[1] + self.floor_rect[3] / 2),
            self.floor_rect[3] / 2
        )
        self.floor.elasticity = 1
        self.floor.friction = 0.5
        self.space.add(self.floor)
        self.circles = []

    def update(self, dt: float) -> None:
        self.space.step(dt)
        self.r.clear()
        for circle in self.circles.copy():
            if circle.body.position[1] > self.size[1] + circle.radius:
                self.circles.remove(circle)
                self.space.remove(circle.body, circle.shape)
            self.r.fill_circle(circle.color, circle.body.position, circle.radius)
            self.r.blit_ex(self.image, dst_rect=(
                circle.body.position[0] - circle.img_offset,
                circle.body.position[1] - circle.img_offset,
                circle.img_size, circle.img_size
            ), angle=circle.body.angle * 180 / math.pi)
        self.r.fill_rect((0, 162, 232), self.floor_rect)
        self.r.blit(self.r.texture_from_surface(
            self.fps_font.render_text(f'FPS: {self.a.clock.get_fps()}', (0, 255, 255), blend=True)
        ), dst_rect=(0, self.fps_font.descent))
        self.r.flip()

    def on_mouse_down(self, event: gg.MouseButtonEvent) -> None:
        circle = Circle(event.pos)
        self.circles.append(circle)
        self.space.add(circle.body, circle.shape)

    def on_key_down(self, event: gg.KeyboardEvent) -> None:
        if event.sym in ('AC Back', 'Escape'):
            self.r.load_scene(main.Scene)

    @staticmethod
    def get_resources() -> tuple:
        return (
            ('font', 'segoeuib.ttf', 50),
            ('image', 'pixelsuftgames.jpg'),
        )

    def destroy(self) -> bool:
        if super().destroy():
            return True
        self.space.remove(self.floor)
        self.fps_font.destroy()
        del self.space
        del self.r
        del self.w
        del self.a
        return False
