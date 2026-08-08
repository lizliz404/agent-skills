#!/usr/bin/env node
/**
 * Regenerate the README "The Packs" icon strip as inline data URIs.
 *
 * Why inline: the README images must render without any network fetch —
 * raw.githubusercontent.com is unreachable from CN networks and GitHub
 * proxies external URLs through camo, both GFW-unreliable. A data URI
 * renders from any network, no host dependency.
 *
 * Usage: node scripts/embed-icons.cjs   (run from repo root)
 * Then review README.md and commit both files.
 */
const fs = require('fs');
const path = require('path');

const names = {
  'doubao-tts.svg': 'Doubao TTS',
  'geo-job-hunt.svg': 'Geo Job Hunt',
  'landing-page-replication-v5.svg': 'Landing Page Replication v5',
  'video-script-conversion.svg': 'Video Script Conversion',
  'design-md-visual-system.svg': 'DESIGN.md Visual System',
  'webgl-threejs-background-animation.svg': 'WebGL Three.js Background Animation',
  'interactive-projects-stream.svg': 'Interactive Projects Stream',
  'seo-master.svg': 'SEO Master',
};

const readmePath = path.join(__dirname, '..', 'README.md');
const assetsDir = path.join(__dirname, '..', 'assets', 'skills');

const lines = Object.keys(names).map((file) => {
  const b64 = fs.readFileSync(path.join(assetsDir, file)).toString('base64');
  return `  <img src="data:image/svg+xml;base64,${b64}" width="48" alt="${names[file]}" />`;
});
const strip = '<p align="center">\n' + lines.join('\n') + '\n</p>';

const readme = fs.readFileSync(readmePath, 'utf8');
const start = readme.indexOf('<p align="center">');
const end = readme.indexOf('</p>', start) + 4;
if (start < 0 || end < 4) {
  console.error('README icon strip not found — did the section change?');
  process.exit(1);
}
fs.writeFileSync(readmePath, readme.slice(0, start) + strip + readme.slice(end));
console.log(`Icon strip regenerated (${Object.keys(names).length} icons).`);
