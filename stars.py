import math
import random
import goodgame as gg
import scene
import main


# Thanks pygame
# https://github.com/pygame/pygame/blob/main/examples/stars.py


class Star:
    def __init__(self, pos: tuple) -> None:
        self.dir = random.randrange(100000)
        self.vel_mult = random.random() * 0.6 + 0.4
        self.vel = [math.sin(self.dir) * self.vel_mult, math.cos(self.dir) * self.vel_mult]
        self.steps = random.randint(1, pos[0])
        self.pos = [pos[0] + (self.vel[0] * self.steps), pos[1] + (self.vel[1] * self.steps)]
        self.vel[0] *= self.steps * 0.09
        self.vel[1] *= self.steps * 0.09


class Scene(scene.Scene):
    def __init__(self, renderer: main.Renderer, data: any) -> None:
        super().__init__(renderer, data)
        self.destroyed = True
        self.should_load = True
        self.a: main.App = renderer.app
        self.w: main.Window = renderer.window
        self.r: main.Renderer = renderer
        self.w.set_resizable(True)
        self.size = self.r.get_output_size()
        self.fps_font: gg.TTF = data[0]
        self.num_stars = 150
        self.center = (self.size[0] / 2, self.size[1] / 2)
        self.timer = gg.Timer(1 / 60, repeat=True, enabled=True, smooth=True)
        self.stars = [Star(self.center) for _ in range(150)]
        self.auto_center = True
        self.destroyed = False
        self.a.clock.reset()

    def update(self, dt: float) -> None:
        self.timer.tick(dt)
        self.r.clear()
        if self.timer.triggered:
            self.timer.triggered -= 1
            for star in self.stars.copy():
                star.pos[0] += star.vel[0]
                star.pos[1] += star.vel[1]
                if self.size[0] > star.pos[0] >= 0 and self.size[1] > star.pos[1] >= 0:
                    star.vel[0] *= 1.05
                    star.vel[1] *= 1.05
                    self.r.draw_point((255, 255, 255), star.pos)
                else:
                    self.stars.remove(star)
                    self.stars.append(Star(self.center))
        else:
            for star in self.stars:
                self.r.draw_point((255, 255, 255), star.pos)
        self.r.blit(self.r.texture_from_surface(
            self.fps_font.render_text(f'FPS: {self.a.clock.get_fps()}', (0, 255, 255), blend=True)
        ), dst_rect=(0, self.fps_font.descent))
        self.r.flip()

    def on_key_down(self, event: gg.KeyboardEvent) -> None:
        if event.sym in ('AC Back', 'Escape'):
            self.r.load_scene(main.Scene)

    def on_resize(self, event: gg.WindowEvent) -> None:
        self.size = self.r.get_output_size()
        if self.auto_center:
            self.center = (self.size[0] / 2, self.size[1] / 2)

    def on_mouse_down(self, event: gg.MouseButtonEvent) -> None:
        self.center = event.pos
        self.auto_center = False

    @staticmethod
    def get_resources() -> tuple:
        return (
            ('font', 'segoeuib.ttf', 50),
        )

    def destroy(self) -> bool:
        if super().destroy():
            return True
        self.fps_font.destroy()
        self.stars.clear()
        del self.r
        del self.w
        del self.a
        return False
