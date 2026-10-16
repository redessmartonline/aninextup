const assert=require('node:assert/strict');
const fs=require('node:fs');

const news=fs.readFileSync('news.html','utf8');
const data=fs.readFileSync('assets/data.js','utf8');
const opm=fs.readFileSync('articles/one-punch-man-season-3-part-2-january-2027.html','utf8');
const nueCover='assets/images/covers/nues-exorcist-official.png';
const opmCover='https://onepunchman-anime.net/news/wp-content/uploads/2026/10/10f7f073197f6d26ac88d6b3ae17f992-566x800.png';

assert(fs.existsSync(nueCover),'official Nue’s Exorcist cover must exist locally');
assert(news.includes('src="'+nueCover+'"'),'news feature should use the existing official cover');
assert(news.includes('src="'+opmCover+'"'),'One-Punch Man news cards should use the official key visual');
assert(data.includes('image:"'+opmCover+'"'),'release data should use the official key visual');
assert(opm.includes('src="'+opmCover+'"'),'article hero and trailer thumbnail should use the official key visual');
assert(!news.includes('https://img2.animatetimes.com/2026/10/0a5da6363fe7b1f7be447ba8bf7a11d26accbb88098481_48559302_b955580253d667871c05979e1fb71d2bb5be8437.jpg'));
assert(!news.includes('https://i.ytimg.com/vi/VR9MRmP2GF8/maxresdefault.jpg'));
console.log('PASS: News and article covers reference verified official artwork, not the generic error fallback.');
