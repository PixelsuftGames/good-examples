import random
import goodgame as gg
import scene
import main


# Thanks pygame
# https://github.com/pygame/pygame/blob/main/examples/go_over_there.py


class Ball:
    def __init__(self, pos: list, speed: float) -> None:
        self.pos = pos
        self.speed = speed


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
        self.num_balls = 200 if self.a.platform == 'Android' else 400
        self.min_speed = 0.25
        self.max_speed = 5
        self.rad = 5
        self.target = ()
        self.fps_font: gg.TTF = data[0]
        self.balls = []
        self.respawn()

    def respawn(self) -> None:
        self.target = ()
        self.balls.clear()
        for i in range(self.num_balls):
            self.balls.append(Ball(
                [random.uniform(0, self.size[0]), random.uniform(0, self.size[1])],
                random.uniform(self.min_speed, self.max_speed)
            ))

    def update(self, dt: float) -> None:
        self.r.clear((31, 143, 65))
        if self.target:
            for ball in self.balls:
                ball.pos[0] += (self.target[0] - ball.pos[0]) * ball.speed * dt
                ball.pos[1] += (self.target[1] - ball.pos[1]) * ball.speed * dt
                self.r.fill_circle((118, 207, 145), ball.pos, self.rad)
        else:
            for ball in self.balls:
                self.r.fill_circle((118, 207, 145), ball.pos, self.rad)
        self.r.blit(self.r.texture_from_surface(
            self.fps_font.render_text(f'FPS: {self.a.clock.get_fps()}', (0, 255, 255), blend=True)
        ), dst_rect=(0, self.fps_font.descent))
        self.r.flip()

    def on_mouse_down(self, event: gg.MouseButtonEvent) -> None:
        if event.pos[0] <= 200 and event.pos[1] <= 100:
            return self.respawn()
        self.target = event.pos

    def on_key_down(self, event: gg.KeyboardEvent) -> None:
        if event.sym in ('AC Back', 'Escape'):
            self.r.load_scene(main.Scene)
        elif event.sym == 'R':
            self.respawn()

    def on_resize(self, event: gg.WindowEvent) -> None:
        self.size = self.r.get_output_size()

    @staticmethod
    def get_resources() -> tuple:
        return (
            ('font', 'segoeuib.ttf', 50),
        )

    def destroy(self) -> bool:
        if super().destroy():
            return True
        self.fps_font.destroy()
        del self.r
        del self.w
        del self.a
        return False
