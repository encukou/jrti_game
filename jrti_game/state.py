import types

state = types.SimpleNamespace(
    zoom=1,
    target_zoom=1,
    alt_zoom_start=None,
    last_drag_pos=None,
    center=[0, 0],
    last_mouse_pos=(0, 0),
    time=0,
)
