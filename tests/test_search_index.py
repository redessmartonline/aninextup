import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('search_builder',Path(__file__).resolve().parents[1]/'scripts/build_search_index.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)

class SearchIndexTests(unittest.TestCase):
    def test_public_articles_aliases_and_unrelated_content(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'articles').mkdir();(root/'assets').mkdir()
            (root/'assets/search-aliases.json').write_text(json.dumps({'/articles/example':['わたしの幸せな結婚','WataKon']}))
            (root/'articles/example.html').write_text('<meta name="description" content="A marriage story"><link rel="canonical" href="https://aninextup.com/articles/example"><article><nav>Navigation noise</nav><h1>My Happy Marriage</h1><p>Searchable main story</p><section class="related-releases"><img src="x"><h3>Unrelated Other Anime</h3></section><script>privateScriptText</script></article><footer>Footer noise</footer>')
            (root/'articles/draft.html').write_text('<meta name="robots" content="noindex,follow"><link rel="canonical" href="https://aninextup.com/articles/draft"><article><h1>Draft</h1></article>')
            (root/'articles/external.html').write_text('<link rel="canonical" href="https://example.com/articles/external"><article><h1>External</h1></article>')
            rows=builder.build(root)['entries'];self.assertEqual(len(rows),1)
            self.assertIn('Searchable main story',rows[0]['content'])
            self.assertEqual(rows[0]['aliases'],['わたしの幸せな結婚','WataKon'])
            for noise in ['Navigation noise','Unrelated Other Anime','privateScriptText','Footer noise']:self.assertNotIn(noise,rows[0]['content'])

    def test_generated_index_covers_every_indexable_article(self):
        result=builder.build();urls=[x['url'] for x in result['entries']]
        self.assertEqual(len(urls),len(set(urls)))
        self.assertEqual(len(urls),len(list((builder.ROOT/'articles').glob('*.html'))))
        for row in result['entries']:
            self.assertTrue(row['title']);self.assertTrue(row['content'])

if __name__=='__main__':unittest.main()
