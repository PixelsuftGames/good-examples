import os
import sys
import math
import random
import datetime
import subprocess
import importlib
import wintheme
import goodgame as gg
import scene


class App(gg.App):
    def __init__(self) -> None:
        super().__init__()
        self.cwd = os.path.dirname(__file__) or os.getcwd()
        self.init(sdl_flags_list=(
            'video', 'events', 'timer', 'audio', 'joystick', 'game_controller'
        ), mixer_formats=('mp3', 'ogg'))
        self.assets_folder = 'assets'
        self.window = Window(self, (1024, 768))
        self.clock = gg.Clock()
        self.window.show()
        self.clock.reset()
        self.run_loop()

    def on_tick(self) -> None:
        self.poll_events()
        if self.running and self.clock.tick():
            self.window.renderer.scene.update(self.clock.delta)

    def on_quit(self, event: gg.QuitEvent = None) -> None:
        super().on_quit(event)
        self.stop_loop()
        self.window.renderer.destroy()
        self.window.destroy()
        self.destroy()


class Window(gg.Window):
    def __init__(self, app: any, size: any) -> None:
        super().__init__(app, size=size)
        self.app: App = self.app
        self.emulate_mouse_with_touch = True
        self.set_min_size((320, 200))
        wintheme.set_window_theme(self.get_hwnd(), wintheme.THEME_DARK)
        self.renderer = Renderer(self)

    def on_resize(self, event: gg.WindowEvent) -> None:  # Hook doesn't work (why?)
        self.renderer.scene.on_resize(event)


class Renderer(gg.Renderer):
    def __init__(self, window: any) -> None:
        bm = gg.BackendManager(window.app)
        if 'GG_BACKEND' in os.environ:
            backend = bm.get_by_name(os.environ['GG_BACKEND'])
        elif '--backend' in sys.argv:
            backend = bm.get_by_name(sys.argv[sys.argv.index('--backend') + 1])
        else:
            backend = bm.get_best()
        super().__init__(window, vsync=True, backend=backend)
        self.app: App = self.app
        self.window: Window = self.window
        self.window.set_title(f'Good Window [{self.backend.name}]')
        self.mixer = gg.Mixer(self.app)
        self.scene = scene.Scene(self, ())
        self.loader = gg.Loader(self.app, Scene.get_resources())
        self.loader.load = self.load_file
        self.loader.run()
        self.loader.call_on_finish(lambda: self.finish_loading(Scene))

    def finish_loading(self, scene_to_load: any) -> None:
        self.scene.destroy()
        self.scene = scene_to_load(self, self.loader.result)
        self.loader.destroy()
        # Not recommended way
        self.window.on_mouse_move = self.scene.on_mouse_move
        self.window.on_mouse_down = self.scene.on_mouse_down
        self.window.on_mouse_up = self.scene.on_mouse_up
        self.window.on_mouse_wheel = self.scene.on_mouse_wheel
        self.window.on_key_down = self.scene.on_key_down
        self.window.on_key_up = self.scene.on_key_up

    def load_scene(self, scene_to_load: any) -> None:
        self.loader = gg.Loader(self.app, scene_to_load.get_resources())
        self.loader.load = self.load_file
        self.loader.run()
        self.loader.call_on_finish(lambda: self.finish_loading(scene_to_load))

    def load_file(self, to_load: tuple) -> any:
        fp = self.app.p(self.app.assets_folder, to_load[1])
        if to_load[0] == 'image':
            return self.app.surface_from_file(fp)
        elif to_load[0] == 'bmp':
            return self.app.surface_from_bmp(fp)
        elif to_load[0] == 'music':
            return gg.Music(self.mixer, fp)
        elif to_load[0] == 'sound':
            return gg.Chunk(self.mixer, fp)
        elif to_load[0] == 'font':
            return gg.TTF(self.app, fp, to_load[2])

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        self.scene.destroy()
        self.window.on_mouse_move = None
        self.window.on_mouse_down = None
        self.window.on_mouse_up = None
        self.window.on_mouse_wheel = None
        self.window.on_key_down = None
        self.window.on_key_up = None
        super().destroy()
        del self.loader
        del self.scene
        return False


class Scene(scene.Scene):
    def __init__(self, renderer: Renderer, data: any) -> None:
        super().__init__(renderer, data)
        self.destroyed = True
        self.a: App = renderer.app
        self.w: Window = renderer.window
        self.r: Renderer = renderer
        self.w.set_icon(data[2])
        self.w.set_resizable(True)
        self.size = self.r.get_output_size()
        self.font: gg.TTF = data[0]
        self.fps_font: gg.TTF = data[1]
        self.bg = self.create_bg_texture()
        self.bg_x_anim = gg.Animation(math.pi * 2, True, True)
        self.bg_x_anim.calc = lambda x: math.sin(x * 2) * 50 - 70
        self.bg_y_anim = gg.Animation(math.pi * 2, True, True)
        self.bg_y_anim.calc = lambda x: math.cos(x * 3) * 50 - 70
        self.bg_r_anim = gg.Animation(math.pi * 2, True, True)
        self.bg_r_anim.calc = lambda x: math.sin(x) * 3
        self.text = ['physics', 'snake', 'colorize', 'stars', 'font', 'chimp']
        if not self.a.platform == 'Android':
            self.text.append('video')
            self.text.append('glcube')
        self.text.sort()
        self.textures = tuple(
            self.r.texture_from_surface(self.font.render_text(x, (255, 0, 0), blend=True)) for x in self.text
        )
        self.tex_h = self.textures[0].get_h()
        self.current = 0
        self.t_anim = gg.Animation(0.25)
        self.t_anim.calc = lambda x: self.current_h1 + (self.current_h2 - self.current_h1) * x * 4
        self.current_h1 = 0
        self.current_h2 = self.size[1] / 2 - self.tex_h / 2 - self.tex_h * self.current
        self.rect = (0, 0, 0, 0)
        self.update_rect()
        self.t_anim.run()
        self.destroyed = False

    def update(self, dt: float) -> None:
        self.bg_x_anim.tick(dt)
        self.bg_y_anim.tick(dt)
        self.bg_r_anim.tick(dt)
        self.t_anim.tick(dt)
        self.r.blit_ex(self.bg, dst_rect=(self.bg_x_anim.value, self.bg_y_anim.value), angle=self.bg_r_anim.value)
        self.r.fill_rect(
            (0, 255, 255),
            self.rect,
            20
        )
        i = self.t_anim.value
        for tex in self.textures:
            self.r.blit(tex, dst_rect=(self.size[0] / 2 - tex.get_w() / 2, i))
            i += self.tex_h
        self.r.blit(self.r.texture_from_surface(
            self.fps_font.render_text(f'FPS: {self.a.clock.get_fps()}', (0, 255, 255), blend=True)
        ), dst_rect=(0, self.fps_font.descent))
        self.r.flip()

    def update_rect(self) -> None:
        self.rect = (
            self.size[0] / 2 - self.textures[self.current].get_w() / 2 - 10, self.size[1] / 2 - self.tex_h / 2,
            self.textures[self.current].get_w() + 20, self.tex_h
        )

    def update_textures(self) -> None:
        self.current_h1 = self.t_anim.value
        self.current_h2 = self.font.descent / 2 + self.size[1] / 2 - self.tex_h / 2 - self.tex_h * self.current
        self.update_rect()
        self.t_anim.reset()
        self.t_anim.run()

    def run_test(self) -> None:
        test_name = self.text[self.current]
        if test_name == 'glcube':
            subprocess.call((sys.executable, self.a.p('glcube.py')))
            return
        self.r.load_scene(importlib.import_module(test_name).Scene)

    def on_mouse_down(self, event: gg.MouseButtonEvent) -> None:
        if event.pos[0] <= 200 and event.pos[1] <= 100:
            self.r.set_vsync(not self.r.vsync)
            return
        if event.pos[0] > self.size[0] / 2:
            return self.run_test()
        self.move(event.pos[1] > self.size[1] / 2)

    def move(self, down: bool) -> None:
        if down:
            if self.current == len(self.text) - 1:
                self.current = -1
            self.current += 1
        else:
            if self.current == 0:
                self.current = len(self.text)
            self.current -= 1
        self.update_textures()

    def on_key_down(self, event: gg.KeyboardEvent) -> None:
        if event.sym in ('AC Back', 'Escape'):
            self.a.on_quit()
        elif event.sym == 'Down':
            self.move(True)
        elif event.sym == 'Up':
            self.move(False)
        elif event.sym in ('Return', 'Space'):
            self.run_test()

    @staticmethod
    def get_resources() -> tuple:
        return (
            ('font', 'segoeuib.ttf', 40),
            ('font', 'segoeuib.ttf', 50),
            ('image', 'pixelsuftgames.jpg')
        )

    def create_bg_texture(self) -> gg.Texture:
        w, h = self.size[0] + 140, self.size[1] + 140
        tex = self.r.create_texture((w, h), self.r.pixel_format_from_str('rgb888'))
        self.r.set_target(tex)
        cube_size = 40
        border = random.uniform(0, 10)
        self.r.clear()
        for y in range(h // cube_size + 1):
            is_filled = not y % 2
            for x in range(w // cube_size + 1):
                if is_filled:
                    self.r.fill_rect((0, 50, 0), (x * cube_size, y * cube_size, cube_size, cube_size), border)
                is_filled = not is_filled
        surf = self.font.render_text(
            f'Pixelsuft, {datetime.datetime.now().year + 1}', (0, 255, 255), (255, 0, 255), True
        )
        self.r.blit(
            self.r.texture_from_surface(surf),
            dst_rect=(w / 2 - surf.w / 2, h - 200)
        )
        self.r.set_target(None)
        return tex

    def on_resize(self, event: gg.WindowEvent) -> None:
        self.size = self.r.get_output_size()
        self.bg = self.create_bg_texture()
        self.update_textures()

    def destroy(self) -> bool:
        if super().destroy():
            return True
        self.fps_font.destroy()
        self.font.destroy()
        del self.r
        del self.w
        del self.a
        return False


if __name__ == '__main__':
    App()
