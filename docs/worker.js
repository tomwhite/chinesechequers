importScripts('https://cdn.jsdelivr.net/pyodide/v0.27.0/full/pyodide.js');

let inputArr;

const SETUP_CODE = `
import sys, time, blessed_mock as _bm

# Pin the injected globals onto the blessed_mock module so they survive runpy's fresh namespace
_bm._input_arr = _input_arr
_bm._post_message = _post_message

# Make play.py's \`from blessed import Terminal\` resolve to our mock
sys.modules['blessed'] = _bm

# Redirect stdout -> postMessage (send immediately on every write)
class _WebStdout:
    def write(self, s):
        if s:
            _bm._post_message({'type': 'output', 'data': s.replace('\\n', '\\r\\n')})
    def flush(self):
        pass

sys.stdout = _WebStdout()

# Patch time.sleep -> Atomics.wait with timeout
def _web_sleep(seconds):
    from js import Atomics, Int32Array, SharedArrayBuffer
    tmp = Int32Array.new(SharedArrayBuffer.new(4))
    Atomics.wait(tmp, 0, 0, int(seconds * 1000))

time.sleep = _web_sleep
`;

self.onmessage = async (e) => {
    if (e.data.type !== 'init') return;

    inputArr = new Int32Array(e.data.inputBuf);
    const pyodide = await loadPyodide();

    // Load game config and fetch Python source files into Pyodide VFS
    const config = await fetch('game.json').then(r => r.json());
    const entry = config.entry ?? 'play.py';

    if (config.packages?.length) {
        self.postMessage({ type: 'output', data: 'Installing packages…\r\n' });
        await pyodide.loadPackage('micropip');
        const micropip = pyodide.pyimport('micropip');
        for (const pkg of config.packages) {
            if (typeof pkg === 'string') {
                await micropip.install(pkg);
            } else {
                await micropip.install(pkg.name, { deps: pkg.deps !== false });
            }
        }
    }

    for (const name of [...config.files, 'blessed_mock.py']) {
        const text = await fetch(name).then(r => r.text());
        pyodide.FS.writeFile(name, text);
    }

    // Expose shared buffer and postMessage to Python
    pyodide.globals.set('_input_arr', inputArr);
    pyodide.globals.set('_post_message', (msg) => self.postMessage(msg.toJs({ dict_converter: Object.fromEntries })));

    // Patch stdout, time.sleep, and blessed
    await pyodide.runPythonAsync(SETUP_CODE);

    self.postMessage({ type: 'ready' });

    try {
        await pyodide.runPythonAsync(`
import runpy
runpy.run_path('${entry}', run_name='__main__')
`);
    } catch (err) {
        // Surface Python exceptions to the terminal
        self.postMessage({ type: 'output', data: '\r\n\x1b[31m' + String(err) + '\x1b[m\r\n' });
    }

    self.postMessage({ type: 'output', data: '\r\n[Game over — refresh to restart]\r\n' });
};
