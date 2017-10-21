from jrti_game.state import state


def mouse_to_logical(mx, my):
    cx, cy = state.center
    lx = (mx - 400) / state.zoom + cx
    ly = (my - 300) / state.zoom + cy
    return lx, ly


def logical_to_mouse(lx, ly):
    cx, cy = state.center
    mx = (lx - cx) * state.zoom + 400
    my = (ly - cy) * state.zoom + 300

    return mx, my


def mouse_to_main_screen(mx, my):
    lx, ly = mouse_to_logical(mx, my)
    return lx - state.main_screen.x, ly - state.main_screen.y


def tool_to_main_screen(tx, ty):
    sx, sy = mouse_to_logical(tx + 400, ty + 300)
    return sx - state.main_screen.x, sy - state.main_screen.y


def tool_to_logical(tx, ty):
    sx, sy = mouse_to_logical(tx + 400, ty + 300)
    return sx, sy
