import goodgame as gg


class Scene:
    def __init__(self, renderer: gg.Renderer, data: any) -> None:
        self.destroyed = False
        self.math = gg.Math()

    @staticmethod
    def get_resources() -> tuple:
        return ()

    def update(self, dt: float) -> None:
        pass

    def on_mouse_move(self, event: gg.MouseMotionEvent) -> None:
        pass

    def on_mouse_down(self, event: gg.MouseButtonEvent) -> None:
        pass

    def on_mouse_up(self, event: gg.MouseButtonEvent) -> None:
        pass

    def on_mouse_wheel(self, event: gg.MouseWheelEvent) -> None:
        pass

    def on_resize(self, event: gg.WindowEvent) -> None:
        pass

    def on_key_down(self, event: gg.KeyboardEvent) -> None:
        pass

    def on_key_up(self, event: gg.KeyboardEvent) -> None:
        pass

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        self.destroyed = True
        return False

    def __del__(self) -> None:
        self.destroy()
