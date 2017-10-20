import sys

if sys.version_info < (3, 5):
    # 3.5 shoud be fine, but don't advertise that...
    text = 'You need Python 3.6+ to play this game.'
else:
    text = 'You should not be seeing this...'

try:
    from pyglet.window import Window
    from pyglet.text import Label
    from pyglet.app import run
    from pyglet.clock import schedule

    window = Window(width=800, height=600)
    label = Label(text)
    label2 = Label('This is Python %s.' %
                   '.'.join(str(x) for x in sys.version_info[:3]))

    @window.event
    def on_draw():
        window.clear()
        label.y = window.height / 2 + (label2.content_height or 30)
        label.x = (window.width - (label.content_width or 0)) / 2
        label.draw()
        label2.y = window.height / 2 - (label2.content_height or 30)
        label2.x = (window.width - (label2.content_width or 0)) / 2
        label2.draw()

    @schedule
    def tick(dt):
        pass

    main = run
except:
    raise RuntimeError(text)
