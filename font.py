import goodgame as gg
import scene
import main


# Mostly thanks pygame


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
        self.ox, self.oy = 0, 0
        self.bg = (195, 195, 195)
        self.heart = self.a.bts(b'\xe2\x99\xa5')
        self.some_unicode = self.a.bts(b'\xe2\x97\x8b\xe2\x99\xa0\xe2\x86\x93\xe2\x99\x80\xe2\x99\xaa')
        self.fps_font: gg.TTF = data[0]
        font1: gg.TTF = data[1]
        font2: gg.TTF = data[2]
        font3: gg.TTF = data[3]
        font4: gg.TTF = data[4]
        font5: gg.TTF = data[5]
        self.tex1 = self.r.texture_from_surface(font1.render_char(self.heart, self.bg, (255, 0, 0), blend=True))
        font1.set_underline(True)
        font1.set_italic(True)
        self.tex2 = self.r.texture_from_surface(font1.render_text('Hello World', (255, 0, 0), self.bg, blend=True))
        font1.set_underline(False)
        font1.set_italic(False)
        self.tex3 = self.r.texture_from_surface(font2.render_text('abcdefghijklm', self.bg, (34, 177, 76), blend=True))
        self.tex4 = self.r.texture_from_surface(font3.render_text_wrapped(
            '\n'.join(tuple('Vertical?')), (63, 72, 204), self.bg, blend=True
        ))
        self.tex5 = self.r.texture_from_surface(font2.render_unicode(
            f'I {self.heart} Unicode! {self.some_unicode}', (0, 162, 232), self.bg, blend=True
        ))
        self.tex6 = self.r.texture_from_surface(font2.render_text('Blend!', (237, 28, 36), blend=True))
        self.tex6.set_alpha_mod(200)
        self.tex6.set_blend_mode('blend')
        self.tex7 = self.r.texture_from_surface(font2.render_text('Mul Blend!', (34, 177, 76), blend=True))
        self.tex7.set_alpha_mod(100)
        self.tex7.set_blend_mode('mul')
        self.tex8 = self.r.texture_from_surface(font2.render_text('Add Blend!', (25, 50, 100), blend=True))
        self.tex8.set_alpha_mod(100)
        self.tex8.set_blend_mode('add')
        font3.set_scale((2, 1))
        self.tex9 = self.r.texture_from_surface(font3.render_text(
            'HORIZONTAL STRETCH!', (0, 0, 255), self.bg, blend=True
        ))
        font3.set_scale((1, 2))
        self.tex10 = self.r.texture_from_surface(font3.render_text(
            'VERTICAL STRETCH!', (255, 0, 0), self.bg, blend=True
        ))
        self.tex11 = self.r.texture_from_surface(font4.render_char(')', (0, 0, 0), blend=True))
        self.tex12 = self.r.texture_from_surface(font5.render_text_wrapped('|\n^\n*', (255, 127, 39), blend=True))
        font5.destroy()
        font4.destroy()
        font3.destroy()
        font2.destroy()
        font1.destroy()
        self.spin1 = gg.Animation(1, repeat=True, enabled=True)
        self.spin1.calc = lambda x: x * 45
        self.spin2 = gg.Animation(1, repeat=True, enabled=True)
        self.spin2.calc = lambda x: x * 30
        self.destroyed = False
        self.a.clock.reset()

    def update(self, dt: float) -> None:
        self.spin1.tick(dt)
        self.spin2.tick(dt)
        self.r.clear(self.bg)
        self.r.blit(self.tex1, dst_rect=(500 + self.ox, 50 + self.oy))
        self.r.blit(self.tex2, dst_rect=(50 + self.ox, 50 + self.oy))
        self.r.blit(self.tex3, dst_rect=(50 + self.ox, 150 + self.oy))
        self.r.blit(self.tex4, dst_rect=(50 + self.ox, 250 + self.oy))
        self.r.blit(self.tex5, dst_rect=(200 + self.ox, 230 + self.oy))
        self.r.blit(self.tex6, dst_rect=(100 + self.ox, 300 + self.oy))
        self.r.blit(self.tex7, dst_rect=(200 + self.ox, 300 + self.oy))
        self.r.blit(self.tex8, dst_rect=(150 + self.ox, 320 + self.oy))
        self.r.blit(self.tex9, dst_rect=(150 + self.ox, 400 + self.oy))
        self.r.blit(self.tex10, dst_rect=(150 + self.ox, 450 + self.oy))
        for angle in range(0, 360, 45):
            self.r.blit_ex(self.tex11, dst_rect=(
                700 + self.ox, 300 + self.oy
            ), angle=angle + self.spin1.value, center=(0, 0))
        for angle in range(15, 375, 30):
            self.r.blit_ex(self.tex12, dst_rect=(
                500 + self.ox, 550 + self.oy
            ), angle=angle + self.spin2.value, center=(0, 0))
        self.r.blit(self.r.texture_from_surface(
            self.fps_font.render_text(f'FPS: {self.a.clock.get_fps()}', (0, 255, 255), blend=True)
        ), dst_rect=(0, self.fps_font.descent))
        self.r.flip()

    def on_key_down(self, event: gg.KeyboardEvent) -> None:
        if event.sym in ('AC Back', 'Escape'):
            self.r.load_scene(main.Scene)

    def on_mouse_move(self, event: gg.MouseMotionEvent) -> None:
        if event.state[0]:
            self.ox += event.rel[0]
            self.oy += event.rel[1]

    def on_resize(self, event: gg.WindowEvent) -> None:
        self.size = self.r.get_output_size()

    @staticmethod
    def get_resources() -> tuple:
        return (
            ('font', 'segoeuib.ttf', 50),
            ('font', 'segoeuib.ttf', 45),
            ('font', 'segoescb.ttf', 45),
            ('font', 'segoeuib.ttf', 30),
            ('font', 'segoescb.ttf', 100),
            ('font', 'segoescb.ttf', 50)
        )

    def destroy(self) -> bool:
        if super().destroy():
            return True
        self.fps_font.destroy()
        del self.r
        del self.w
        del self.a
        return False
