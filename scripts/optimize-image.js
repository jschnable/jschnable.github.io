#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
let sharp;

try {
  sharp = require('sharp');
} catch (error) {
  console.error('The "sharp" dependency is missing. Run `npm install` before optimizing images.');
  process.exit(1);
}

const [, , inputPath, outputPath] = process.argv;

if (!inputPath) {
  console.error('Usage: npm run optimize:image -- <input-image> [output-image]');
  process.exit(1);
}

const source = path.resolve(process.cwd(), inputPath);
const target = path.resolve(process.cwd(), outputPath || inputPath);

if (!fs.existsSync(source)) {
  console.error(`✖ Cannot find file: ${source}`);
  process.exit(1);
}

const allowedExtensions = new Set(['.jpg', '.jpeg', '.png', '.webp']);
const extension = path.extname(target).toLowerCase();

if (!allowedExtensions.has(extension)) {
  console.error(`✖ Unsupported file type "${extension}". Use JPG, PNG, or WEBP.`);
  process.exit(1);
}

const formatBytes = (bytes) => {
  const units = ['B', 'KB', 'MB'];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const size = bytes / Math.pow(1024, index);
  return `${size.toFixed(1)} ${units[index]}`;
};

const optimize = async () => {
  const beforeStats = await fs.promises.stat(source);
  const tempFile = path.join(path.dirname(target), `.tmp-${Date.now()}${extension}`);

  let pipeline = sharp(source).rotate().resize({ width: 1800, withoutEnlargement: true }).withMetadata();

  switch (extension) {
    case '.png':
      pipeline = pipeline.png({ compressionLevel: 9, adaptiveFiltering: true });
      break;
    case '.webp':
      pipeline = pipeline.webp({ quality: 82 });
      break;
    default:
      pipeline = pipeline.jpeg({ quality: 82, mozjpeg: true });
  }

  await pipeline.toFile(tempFile);
  await fs.promises.rename(tempFile, target);

  const afterStats = await fs.promises.stat(target);
  console.log(`✔ Optimized ${path.basename(target)}: ${formatBytes(beforeStats.size)} → ${formatBytes(afterStats.size)}`);
};

optimize().catch((error) => {
  console.error('✖ Image optimization failed:', error.message);
  process.exit(1);
});
