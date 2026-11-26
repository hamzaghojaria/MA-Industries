/** Generate the catalogue PDF using the current website catalogue data. */
import { execFileSync } from 'node:child_process';
import { access, mkdir, writeFile } from 'node:fs/promises';
import { constants } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadCatalogue } from '../site/catalogue-markup.mjs';

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const catalogue = await loadCatalogue();
if (!catalogue || !Array.isArray(catalogue.papers) || !Array.isArray(catalogue.categories)) {
  throw new Error('Catalogue data is missing products or categories.');
}

const tempDirectory = resolve(ROOT, 'tmp/pdfs');
await mkdir(tempDirectory, { recursive: true });
await writeFile(resolve(tempDirectory, 'catalogue-data.json'), JSON.stringify(catalogue));

const bundledPython = resolve(ROOT, 'tmp/pdf-venv/Scripts/python.exe');
let python = process.env.PYTHON?.trim() || 'python';
let pythonArgs = [];
try {
  await access(bundledPython, constants.X_OK);
  if (!process.env.PYTHON) python = bundledPython;
  await execFileSync(python, ['-c', 'import pymupdf, reportlab, PIL'], { stdio: 'ignore' });
} catch {
  // A stale bundled environment can still contain an interpreter but lack its packages.
  // Use uv's managed temporary environment when it is available.
  if (!process.env.PYTHON && process.platform === 'win32') {
    python = 'uv';
    pythonArgs = ['run', '--with', 'reportlab', '--with', 'pillow', '--with', 'pymupdf', 'python'];
  }
}

execFileSync(python, [...pythonArgs, resolve(ROOT, 'scripts/catalogue/create-focused-catalogue.py'), ...process.argv.slice(2)], {
  cwd: ROOT,
  stdio: 'inherit'
});
