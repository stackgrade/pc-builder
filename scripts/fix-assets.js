/**
 * Post-build script to fix GitHub Pages asset serving
 * Replaces @ in filenames with -at- and updates HTML references
 */

import { readFileSync, writeFileSync, readdirSync, cpSync, rmSync } from 'fs';
import { join } from 'path';

const distDir = 'dist';

console.log('Fixing GitHub Pages asset issues...');

// Read the built index.html
const htmlPath = join(distDir, 'index.html');
let html = readFileSync(htmlPath, 'utf-8');

// Find and rename _astro files with @ in name
const astroDir = join(distDir, '_astro');
try {
  const files = readdirSync(astroDir);
  
  for (const file of files) {
    if (file.includes('@')) {
      const oldPath = join(astroDir, file);
      const newFile = file.replace('@', '-at-');
      const newPath = join(astroDir, newFile);
      
      // Rename file
      cpSync(oldPath, newPath);
      rmSync(oldPath);
      
      console.log(`Renamed: ${file} -> ${newFile}`);
      
      // Update HTML references
      html = html.replace(`/_astro/${file}`, `/_astro/${newFile}`);
    }
  }
} catch (e) {
  console.log('No _astro directory or no @ files');
}

// Write fixed HTML
writeFileSync(htmlPath, html);
console.log('Fixed index.html references');
console.log('Done!');
