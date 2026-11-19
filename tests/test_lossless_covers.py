from pathlib import Path
import sys
import subprocess
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from optimize_public_covers import encode_lossless, optimize_img, replace_image_values
from PIL import Image


class LosslessCoverTests(unittest.TestCase):
    def test_every_decoded_pixel_and_png_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            png=Path(directory)/'guide.png'
            image=Image.new('RGB',(1200,630))
            image.putdata([((x*13)%256,(x//1200)%256,(x//17)%256) for x in range(1200*630)])
            image.save(png,compress_level=0)
            before=png.read_bytes()
            webp=encode_lossless(png)
            self.assertIsNotNone(webp)
            self.assertEqual(before,png.read_bytes())
            with Image.open(webp) as decoded:
                self.assertEqual(decoded.size,image.size)
                self.assertEqual(decoded.convert('RGB').tobytes(),image.tobytes())
            self.assertLess(webp.stat().st_size,png.stat().st_size)

    def test_static_src_and_dimensions_remain_unchanged(self):
        import re
        source='<img src="/assets/article-covers/guide.png" width="1200" height="630" loading="lazy">'
        mapping={'/assets/article-covers/guide.png':'/assets/article-covers/guide.webp'}
        result=re.sub(r'<img\b[^>]*>',lambda m:optimize_img(m,mapping),source)
        self.assertIn('src="/assets/article-covers/guide.png"',result)
        self.assertIn('srcset="/assets/article-covers/guide.webp 1x"',result)
        self.assertIn('width="1200" height="630"',result)

    def test_webp_error_retries_png_before_generic_fallback(self):
        script = r"""
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync(process.argv[1],'utf8').split('function publicArticleCover')[0];
class ImageElement {
 constructor(){this.src='https://aninextup.com/assets/article-covers/guide.png';this.currentSrc='https://aninextup.com/assets/article-covers/guide.webp';this.dataset={};this.classList={add(){}};this.srcset='webp';}
 removeAttribute(name){delete this[name];}
}
const context={HTMLImageElement:ImageElement,URL,location:{origin:'https://aninextup.com'}};
vm.createContext(context);vm.runInContext(source+';globalThis.fallback=useCardImageFallback;',context);
const image=new ImageElement();context.fallback(image);
assert.strictEqual(image.src,'https://aninextup.com/assets/article-covers/guide.png');
assert.strictEqual(image.srcset,undefined);
image.currentSrc=image.src;context.fallback(image);
assert.strictEqual(image.src,'/assets/images/anime-image-fallback.svg');
"""
        app=Path(__file__).resolve().parents[1]/'assets/app.js'
        subprocess.run(['node','-e',script,str(app)],check=True)

    def test_runtime_feed_changes_images_without_touching_links(self):
        data={'image':'/assets/article-covers/guide.png','url':'/articles/guide',
              'items':[{'cover':'/assets/article-covers/guide.png'}]}
        replace_image_values(data,{'/assets/article-covers/guide.png':'/assets/article-covers/guide.webp'})
        self.assertEqual(data['image'],'/assets/article-covers/guide.webp')
        self.assertEqual(data['items'][0]['cover'],'/assets/article-covers/guide.webp')
        self.assertEqual(data['url'],'/articles/guide')


if __name__=='__main__':unittest.main()
