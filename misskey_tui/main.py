from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError

from misskey_tui.model import MkAPIs
from misskey_tui.scenes import SCENES

def wrapper(screen:Screen, last_scene:Scene, vm):
    scene = [Scene([v[0](screen, vm[i])], -1, name=v[2]) for i, v in enumerate(SCENES)]
    screen.play(scenes=scene,
                stop_on_resize=True,
                start_scene=last_scene,
                allow_int=True)

def main():
    msk = MkAPIs()
    view_models = [i[1](msk) for i in SCENES]
    last_scene = None
    try:
        while True:
            try:
                Screen.wrapper(wrapper, arguments=[last_scene, view_models])
                break
            except ResizeScreenError as e:
                last_scene = e.scene
    except:
        raise
    # finally:
    #     msk._finds()

if __name__ == "__main__":
    main()