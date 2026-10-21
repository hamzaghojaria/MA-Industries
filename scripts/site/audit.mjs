/** Read-only repository inventory: tracked generated files, asset references and sizes. */
import { readdir, readFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { ROOT } from './config.mjs';
import { loadCatalogue } from './catalogue-markup.mjs';

const files = [];
async function walk(dir = '') {
  for (const entry of await readdir(new URL(dir || '.', ROOT), { withFileTypes: true })) {
    if (['.git', '.uv-cache', '.uv-python', 'node_modules', 'dist', 'tmp'].includes(entry.name)) continue;
    const path = dir + entry.name;
    if (entry.isDirectory()) await walk(path + '/');
    else files.push(path);
  }
}
await walk();
const texts = await Promise.all(files.filter(file => /\.(?:html|m?js|css|py|json|md|yaml)$/.test(file))
  .map(async file => [file, await readFile(new URL(file, ROOT), 'utf8')]));
const catalogue = await loadCatalogue();
const referenced = texts.map(([, text]) => text).join('\n');
const unused = files.filter(file => file.startsWith('assets/') && !referenced.includes(file) && !referenced.includes(file.split('/').at(-1)));
const hashes = new Map();
let assetBytes = 0;
for (const file of files.filter(file => file.startsWith('assets/'))) {
  const bytes = await readFile(new URL(file, ROOT));
  assetBytes += bytes.length;
  const hash = createHash('sha256').update(bytes).digest('hex');
  hashes.set(hash, [...(hashes.get(hash) || []), file]);
}
const tracked = execFileSync('git', ['ls-files', 'tmp', 'output'], { cwd: ROOT, encoding: 'utf8' }).trim().split('\n');
const report = {
  sourceFiles: files.length, assetBytes, unreferencedCandidates: unused,
  exactDuplicates: [...hashes.values()].filter(group => group.length > 1),
  trackedGeneratedFiles: tracked,
  catalogueSpecifications: catalogue.papers.filter(p => catalogue.categories.find(g => g.id === p.group)?.collection)
    .map(p => ({ id: p.id, name: p.name, specifications: p.specifications || [] }))
};
console.log(JSON.stringify(report, null, 2));
