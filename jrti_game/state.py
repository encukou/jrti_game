import types
import random

import pyglet

from jrti_game.data import default_keymap


state = types.SimpleNamespace(
    zoom=1,
    target_zoom=1,
    alt_zoom_start=None,
    last_drag_pos=None,
    center=[0, 0],
    last_mouse_pos=(400, 300),
    time=0,
    tool=None,
    tool_x=0,
    tool_y=0,
    reassign_state=None,
    reassign_anim_start=0,
    keymap={getattr(pyglet.window.key, k): v
            for k, v in default_keymap.items()},
    code=[random.randrange(10) for i in range(4)],
    key_config=[0, 3, 4, 0],
    stuck_keys=[],
    ending=False,
    min_zoom=1,
    end_time=None,
    zoom_easing=1,
)
