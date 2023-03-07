import random
import goodgame as gg
import scene
import main


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
        self.scale = (self.size[0] / 640, self.size[1] / 480)
        self.avg_scale = (self.scale[0] + self.scale[1]) / 2
        self.cell_size = (20 * self.scale[0], 20 * self.scale[1])
        self.apple_rad = (self.cell_size[0] / 2, self.cell_size[1] / 2)
        self.field_size = (32, 24)
        self.fps_font: gg.TTF = data[0]
        self.font: gg.TTF = data[1]
        self.music: gg.Music = data[2]
        self.eat_sound: gg.Chunk = data[3]
        self.die_sound: gg.Chunk = data[4]
        self.min_tick = 0.06 if self.a.platform == 'Android' else 0.04
        self.timer = gg.Timer(0.75, enabled=True, smooth=True)
        self.die_timer = gg.Timer(2.5)
        self.snake = [(5, 1), (4, 1), (3, 1), (2, 1)]
        self.score = 0
        self.snake_len = len(self.snake) - 1
        self.score_tex = self.r.texture_from_surface(self.font.render_text('Score: 0', (0, 255, 255), blend=True))
        self.score_pos = (self.size[0] - self.score_tex.get_w() - 5, -12)
        self.apple_pos = (5, 5)
        self.music.set_volume(0.5)
        self.dir = 0
        self.new_dir = 0
        self.destroyed = False
        self.a.clock.reset()
        self.music.play(-1)

    def update_score(self) -> None:
        self.snake_len += 1
        self.score += 1
        while self.apple_pos in self.snake:
            self.apple_pos = (random.randint(0, self.field_size[0] - 1), random.randint(0, self.field_size[1] - 1))
        self.timer.duration = max(self.timer.duration - 0.01, self.min_tick)
        self.score_tex = self.r.texture_from_surface(self.font.render_text(
            f'Score: {self.score}', (0, 255, 255), blend=True
        ))
        self.score_pos = (self.size[0] - self.score_tex.get_w() - 5, -12)
        self.eat_sound.play()

    def game_over(self) -> None:
        self.die_timer.run()
        self.music.stop()
        self.die_sound.play()

    def update(self, dt: float) -> None:
        self.timer.tick(dt)
        if self.die_timer.enabled:
            self.die_timer.tick(dt)
            if self.die_timer.triggered:
                self.a.clock.speed_hack = 1
                return self.r.load_scene(main.Scene)
        elif self.timer.triggered:
            self.timer.triggered -= 1
            last_cache = self.snake.pop(-1)
            self.snake.insert(1, self.snake[0])
            self.dir = self.new_dir
            if self.dir == 0:
                self.snake[0] = (self.snake[0][0] + 1, self.snake[0][1])
            elif self.dir == 1:
                self.snake[0] = (self.snake[0][0], self.snake[0][1] + 1)
            elif self.dir == 2:
                self.snake[0] = (self.snake[0][0] - 1, self.snake[0][1])
            elif self.dir == 3:
                self.snake[0] = (self.snake[0][0], self.snake[0][1] - 1)
            if self.snake[0] in self.snake[1:] or self.snake[0][0] < 0 or self.snake[0][1] < 0 or \
                    self.snake[0][0] >= self.field_size[0] or self.snake[0][1] >= self.field_size[1]:
                self.game_over()
                return
            if self.snake[0] == self.apple_pos:
                self.snake.append(last_cache)
                self.update_score()
        self.r.clear()
        self.r.fill_ellipse_tl((255, 0, 0), (self.apple_pos[0] * self.cell_size[0],
                                             self.apple_pos[1] * self.cell_size[1]), self.apple_rad[0],
                               self.apple_rad[1])
        for snake_part in self.snake[1:]:
            self.r.fill_rect((0, 255, 0), (snake_part[0] * self.cell_size[0], snake_part[1] * self.cell_size[1],
                                           self.cell_size[0], self.cell_size[1]), 5 * self.avg_scale)
        self.r.fill_rect((255, 0, 0), (self.snake[0][0] * self.cell_size[0], self.snake[0][1] * self.cell_size[1],
                                       self.cell_size[0], self.cell_size[1]), 5 * self.avg_scale)
        self.r.blit(self.r.texture_from_surface(
            self.fps_font.render_text(f'FPS: {self.a.clock.get_fps()}', (0, 255, 255), blend=True)
        ), dst_rect=(0, self.fps_font.descent))
        self.r.blit(self.score_tex, dst_rect=self.score_pos)
        self.r.flip()

    def on_mouse_down(self, event: gg.MouseButtonEvent) -> None:
        if event.pos[0] <= 200 and event.pos[1] <= 100:
            self.a.clock.speed_hack = 4
            return
        if event.pos[0] > self.size[0] / 2:
            if event.pos[1] > self.size[1] / 2:
                if self.dir in (0, 2):
                    self.new_dir = 1
            elif self.dir in (0, 2):
                self.new_dir = 3
        elif event.pos[0] > self.size[0] / 4:
            if self.dir in (1, 3):
                self.new_dir = 0
        elif self.dir in (1, 3):
            self.new_dir = 2

    def on_mouse_up(self, event: gg.MouseButtonEvent) -> None:
        self.a.clock.speed_hack = 1

    def on_key_down(self, event: gg.KeyboardEvent) -> None:
        if event.sym in ('AC Back', 'Escape'):
            self.r.load_scene(main.Scene)
        elif event.sym == 'Right':
            if self.dir in (1, 3):
                self.new_dir = 0
        elif event.sym == 'Down':
            if self.dir in (0, 2):
                self.new_dir = 1
        elif event.sym == 'Left':
            if self.dir in (1, 3):
                self.new_dir = 2
        elif event.sym == 'Up':
            if self.dir in (0, 2):
                self.new_dir = 3

    def on_resize(self, event: gg.WindowEvent) -> None:
        self.size = self.r.get_output_size()
        self.scale = (self.size[0] / 640, self.size[1] / 480)
        self.avg_scale = (self.scale[0] + self.scale[1]) / 2
        self.cell_size = (20 * self.scale[0], 20 * self.scale[1])
        self.apple_rad = (self.cell_size[0] / 2, self.cell_size[1] / 2)
        self.score_pos = (self.size[0] - self.score_tex.get_w() - 5, -12)

    @staticmethod
    def get_resources() -> tuple:
        return (
            ('font', 'segoeuib.ttf', 50),
            ('font', 'segoescb.ttf', 50),
            ('music', 'snake_music.mp3'),
            ('sound', 'snake_eat.ogg'),
            ('sound', 'snake_die.ogg')
        )

    def destroy(self) -> bool:
        if super().destroy():
            return True
        self.music.destroy()
        self.eat_sound.destroy()
        self.die_sound.destroy()
        self.font.destroy()
        self.fps_font.destroy()
        del self.r
        del self.w
        del self.a
        return False
