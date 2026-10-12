// Reads a JSON array of TeX strings on stdin, writes a JSON array of rendered HTML strings.
const katex = require('katex');
let buf = '';
process.stdin.on('data', (d) => { buf += d; });
process.stdin.on('end', () => {
  const list = JSON.parse(buf);
  const out = list.map((tex) => {
    try {
      return katex.renderToString(tex, { displayMode: true, throwOnError: true, strict: false, output: 'htmlAndMathml' });
    } catch (e) {
      return 'ERROR: ' + e.message;
    }
  });
  process.stdout.write(JSON.stringify(out));
});
