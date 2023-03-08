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
        self.fps_font: gg.TTF = data[0]
        self.images = tuple(data[1:])
        self.current_id = 0
        self.tex_w = 0
        self.texture = self.create_texture()
        self.colors = ((0, 0, 255), (255, 0, 255), (255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255))
        self.color_id = 1
        self.from_color = self.colors[0]
        self.color = gg.Animation(4, enabled=True)
        self.color.calc = self.calc
        self.color_speed = (
            (self.colors[1][0] - self.from_color[0]) / self.color.duration,
            (self.colors[1][1] - self.from_color[1]) / self.color.duration,
            (self.colors[1][2] - self.from_color[2]) / self.color.duration
        )
        self.bg_anim = gg.Animation(5, repeat=True, enabled=True)
        self.bg_anim.calc = lambda x: -self.tex_w / self.bg_anim.duration * x
        self.destroyed = False
        self.a.clock.reset()

    def calc(self, x: float) -> tuple:
        return self.from_color[0] + x * self.color_speed[0],\
            self.from_color[1] + x * self.color_speed[1],\
            self.from_color[2] + x * self.color_speed[2]

    def update(self, dt: float) -> None:
        self.bg_anim.tick(dt)
        self.color.tick(dt)
        if not self.color.enabled:
            self.color_id += 1
            if self.color_id >= len(self.colors):
                self.color_id = 0
            self.from_color = self.color.value
            self.color_speed = (
                (self.colors[self.color_id][0] - self.from_color[0]) / self.color.duration,
                (self.colors[self.color_id][1] - self.from_color[1]) / self.color.duration,
                (self.colors[self.color_id][2] - self.from_color[2]) / self.color.duration
            )
            self.color.run()
        self.texture.set_color_mod(self.color.value)
        self.r.blit(self.texture, dst_rect=(self.bg_anim.value, 0))
        self.r.blit(self.r.texture_from_surface(
            self.fps_font.render_text(f'FPS: {self.a.clock.get_fps()}', (0, 255, 255), blend=True)
        ), dst_rect=(0, self.fps_font.descent))
        self.r.flip()

    def create_texture(self) -> gg.Texture:
        surf: gg.Surface = self.images[self.current_id]
        tex: gg.Texture = self.r.texture_from_surface(surf)
        tex.set_scale_mode('linear')
        scale = self.size[1] / surf.h
        w_scale = surf.w * scale
        result = self.r.create_texture((
            int(self.size[0] / w_scale + 2) * w_scale,
            surf.h
        ), self.r.pixel_format_from_str('rgb888'))
        self.r.set_target(result)
        for x in range(int(result.get_w() // w_scale) + 1):
            self.r.blit(tex, dst_rect=(x * w_scale, 0, w_scale, self.size[1]))
        self.r.set_target(None)
        self.tex_w = w_scale
        return result

    def next(self) -> None:
        self.current_id += 1
        if self.current_id >= len(self.images):
            self.current_id = 0
        self.texture = self.create_texture()

    def on_key_down(self, event: gg.KeyboardEvent) -> None:
        if event.sym in ('AC Back', 'Escape'):
            self.r.load_scene(main.Scene)
        elif event.sym in ('Space', 'Return'):
            self.next()

    def on_mouse_down(self, event: gg.MouseButtonEvent) -> None:
        self.next()

    def on_resize(self, event: gg.WindowEvent) -> None:
        self.size = self.r.get_output_size()
        self.texture = self.create_texture()

    @staticmethod
    def get_resources() -> tuple:
        return (
            ('font', 'segoeuib.ttf', 50),
        ) + tuple(('image', f'game_bg_0{x}_001-hd.png') for x in range(1, 10)) +\
            tuple(('image', f'game_bg_{x}_001-hd.png') for x in range(10, 20))

    def destroy(self) -> bool:
        if super().destroy():
            return True
        self.fps_font.destroy()
        del self.r
        del self.w
        del self.a
        return False
