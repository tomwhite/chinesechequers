import sys
from contextlib import contextmanager

# _input_arr is injected by worker.js via pyodide.globals.set('_input_arr', ...)


def _read_key():
    from js import Atomics
    Atomics.wait(_input_arr, 0, 0)          # block until index 0 != 0
    length = int(_input_arr[1])
    data = bytes(int(_input_arr[2 + i]) for i in range(length))
    Atomics.store(_input_arr, 0, 0)        # reset for next key
    return data


class Keystroke:
    def __init__(self, code=None, value=''):
        self.code = code
        self._value = value

    def lower(self):
        return self._value.lower()

    def __str__(self):
        return self._value


class Terminal:
    KEY_LEFT  = 'KEY_LEFT'
    KEY_RIGHT = 'KEY_RIGHT'
    KEY_UP    = 'KEY_UP'
    KEY_DOWN  = 'KEY_DOWN'
    KEY_ENTER = 'KEY_ENTER'

    def inkey(self):
        data = _read_key()
        MAP = {
            b'\x1b[A': self.KEY_UP,
            b'\x1b[B': self.KEY_DOWN,
            b'\x1b[C': self.KEY_RIGHT,
            b'\x1b[D': self.KEY_LEFT,
            b'\r':     self.KEY_ENTER,
            b'\n':     self.KEY_ENTER,
        }
        code = MAP.get(data)
        return Keystroke(code=code, value=data.decode('utf-8', errors='replace'))

    def move(self, y, x):
        return f'\033[{y+1};{x+1}H'

    def reverse(self, s):
        return f'\033[7m{s}\033[m'

    def clear(self):
        # blessed's Terminal.clear returns a string but doesn't print it when called
        # with no args, so play.py's term.clear() statement is effectively a no-op
        return ''

    def fullscreen(self):
        @contextmanager
        def _ctx():
            sys.stdout.write('\033[?1049h\033[H')
            sys.stdout.flush()
            try:
                yield
            finally:
                sys.stdout.write('\033[?1049l')
                sys.stdout.flush()
        return _ctx()

    def hidden_cursor(self):
        @contextmanager
        def _ctx():
            sys.stdout.write('\033[?25l')
            sys.stdout.flush()
            try:
                yield
            finally:
                sys.stdout.write('\033[?25h')
                sys.stdout.flush()
        return _ctx()

    def cbreak(self):
        @contextmanager
        def _ctx():
            yield
        return _ctx()

    @property
    def width(self):
        return 80

    @property
    def height(self):
        return 24
