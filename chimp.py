import math
import goodgame as gg
import scene
import main


# Thanks to pygame
# https://github.com/pygame/pygame/blob/main/examples/chimp.py


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
        self.font: gg.TTF = data[1]
        try:
            self.font.set_wrapped_align('center')
        except RuntimeError:
            pass
        self.text_tex = self.r.texture_from_surface(self.font.render_text_wrapped(
            'Pummel The Chimp, And Win $$$', (0, 0, 0), blend=True, wrap_length=self.size[0]
        ))
        self.whiff_sound: gg.Chunk = data[2]
        self.punch_sound: gg.Chunk = data[3]
        self.fist_tex = self.r.texture_from_surface(data[4])
        self.chimp_tex = self.r.texture_from_surface(data[5])
        self.fist_offset = (235, 80)
        self.chimp_pos = [0, 200]
        self.y_anim = gg.Animation(math.pi * 2, repeat=True, enabled=True)
        self.y_anim.calc = lambda x: 50 + math.sin(x * 5) * 100
        self.chimp_size = (61 * 2, 89 * 2)
        self.chimp_left = False
        self.chimp_speed = 1000
        self.fist_pos = (0, 0)
        self.skip_touch = not self.a.platform == 'Android'
        self.rot_anim = gg.Animation(0.25)
        self.rot_anim.calc = lambda x: x * 1440
        self.rot_anim.value = 0
        if self.skip_touch:
            self.a.set_rel_mouse(True)
        self.destroyed = False
        self.a.clock.reset()

    def update(self, dt: float) -> None:
        self.y_anim.tick(dt)
        self.rot_anim.tick(dt)
        if not self.rot_anim.enabled:
            if self.chimp_left:
                self.chimp_pos[0] -= dt * self.chimp_speed
                if self.chimp_pos[0] <= 0:
                    self.chimp_left = False
            else:
                self.chimp_pos[0] += dt * self.chimp_speed
                if self.chimp_pos[0] + self.chimp_size[0] > self.size[0]:
                    self.chimp_left = True
        self.r.clear((170, 238, 187))
        self.r.blit_ex(self.chimp_tex, dst_rect=(
            self.chimp_pos[0], self.chimp_pos[1] + self.y_anim.value, self.chimp_size[0], self.chimp_size[1]
        ), angle=self.rot_anim.value, flip_horizontal=self.chimp_left)
        self.r.blit(self.text_tex, dst_rect=(self.size[0] / 2 - self.text_tex.get_w() / 2, 30))
        self.r.blit(
            self.fist_tex, dst_rect=(self.fist_pos[0] - self.fist_offset[0], self.fist_pos[1] - self.fist_offset[1])
        )
        self.r.blit(self.r.texture_from_surface(
            self.fps_font.render_text(f'FPS: {self.a.clock.get_fps()}', (0, 255, 255), blend=True)
        ), dst_rect=(0, self.fps_font.descent))
        self.r.flip()

    def on_mouse_down(self, event: gg.MouseButtonEvent) -> None:
        self.fist_pos = event.pos
        if self.rot_anim.enabled or self.whiff_sound.is_playing() or self.punch_sound.is_playing():
            return
        if self.math.point_in_rect(
                (self.chimp_pos[0], self.chimp_pos[1], self.chimp_size[0], self.chimp_size[1]), self.fist_pos
        ):
            self.rot_anim.run()
            self.punch_sound.play()
        else:
            self.whiff_sound.play()

    def on_mouse_move(self, event: gg.MouseMotionEvent) -> None:
        if self.skip_touch or event.state[0]:
            self.fist_pos = event.pos

    def on_key_down(self, event: gg.KeyboardEvent) -> None:
        if event.sym in ('AC Back', 'Escape'):
            self.a.set_rel_mouse(False)
            self.r.load_scene(main.Scene)

    def on_resize(self, event: gg.WindowEvent) -> None:
        self.size = self.r.get_output_size()
        self.text_tex = self.r.texture_from_surface(self.font.render_text_wrapped(
            'Pummel The Chimp, And Win $$$', (0, 0, 0), blend=True, wrap_length=self.size[0]
        ))

    @staticmethod
    def get_resources() -> tuple:
        return (
            ('font', 'segoeuib.ttf', 50),
            ('font', 'segoescb.ttf', 50),
            ('sound', 'whiff.ogg'),
            ('sound', 'punch.ogg'),
            ('image', 'fist.png'),
            ('image', 'chimp.png')
        )

    def destroy(self) -> bool:
        if super().destroy():
            return True
        self.whiff_sound.destroy()
        self.punch_sound.destroy()
        self.font.destroy()
        self.fps_font.destroy()
        del self.r
        del self.w
        del self.a
        return False
