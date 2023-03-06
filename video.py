import goodgame as gg
import scene
import main
import cv2


class Scene(scene.Scene):
    def __init__(self, renderer: main.Renderer, data: any) -> None:
        super().__init__(renderer, data)
        self.destroyed = True
        self.should_load = True
        self.a: main.App = renderer.app
        self.w: main.Window = renderer.window
        self.r: main.Renderer = renderer
        self.w.set_resizable(True)
        self.fps_font: gg.TTF = data[0]
        self.music: gg.Music = data[1]
        self.circles = []
        # Not Recommended, but we don't need to check cv2
        self.cap = cv2.VideoCapture(self.a.p(self.a.assets_folder, 'video.mp4'))  # noqa
        # You can get everything from cap, by I'm lazy)
        self.format = self.r.pixel_format_from_str('bgr24')
        self.fps = 25
        self.limit = 1 / self.fps
        self.size = (960, 720)
        self.pitch = 3 * self.size[0]
        self.tex = self.r.create_texture(self.size, self.format)
        self.update_frame()
        self.timer = gg.Timer(self.limit, enabled=True, smooth=True)
        self.destroyed = False
        self.a.clock.reset()
        self.music.play()

    def update(self, dt: float) -> None:
        self.timer.tick(dt)
        if self.timer.triggered:
            self.timer.triggered -= 1
            self.update_frame()
        self.r.blit(self.tex)
        self.r.blit(self.r.texture_from_surface(
            self.fps_font.render_text(f'FPS: {self.a.clock.get_fps()}', (0, 255, 255), blend=True)
        ), dst_rect=(0, self.fps_font.descent))
        self.r.flip()

    def update_frame(self) -> None:
        ret, frame = self.cap.read()
        if not ret:
            if self.should_load:
                self.should_load = False
                self.r.load_scene(main.Scene)
            return
        self.tex.update(frame.ctypes.data, self.pitch)

    def on_key_down(self, event: gg.KeyboardEvent) -> None:
        if event.sym in ('AC Back', 'Escape'):
            self.r.load_scene(main.Scene)

    @staticmethod
    def get_resources() -> tuple:
        return (
            ('font', 'segoeuib.ttf', 50),
            ('music', 'video_music.mp3')
        )

    def destroy(self) -> bool:
        if super().destroy():
            return True
        self.cap.release()
        self.music.destroy()
        self.fps_font.destroy()
        del self.r
        del self.w
        del self.a
        return False
