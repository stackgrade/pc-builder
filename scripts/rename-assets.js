/**
 * Post-build script: removes @ from asset filenames and updates HTML references
 */

import { readFileSync, writeFileSync, readdirSync, cpSync, rmSync } from 'fs';
import { join } from 'path';

const distDir = 'dist';

console.log('Removing @ from asset filenames...\n');

// Find and rename files with @ in name
function renameInDir(dir) {
  try {
    const files = readdirSync(dir);
    
    for (const file of files) {
      const fullPath = join(dir, file);
      
      // Recurse into subdirectories
      if (file.includes('.') === false) {
        renameInDir(fullPath);
        continue;
      }
      
      if (file.includes('@')) {
        const newFile = file.replace(/@/g, '-a-');
        const oldPath = fullPath;
        const newPath = join(dir, newFile);
        
        cpSync(oldPath, newPath);
        rmSync(oldPath);
        
        console.log(`Renamed: ${file} -> ${newFile}`);
        
        // Update HTML references
        const indexPath = join(distDir, 'index.html');
        let html = readFileSync(indexPath, 'utf-8');
        html = html.replaceAll(`/${file}`, `/${newFile}`);
        writeFileSync(indexPath, html);
      }
    }
  } catch (e) {
    // Directory doesn't exist
  }
}

renameInDir(distDir);
console.log('\nDone!');
