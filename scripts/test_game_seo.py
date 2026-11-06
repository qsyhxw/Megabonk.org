import unittest,sys,json
from pathlib import Path
from unittest.mock import patch
from game_seo import candidates,edit,ROOT
class GameSeoTests(unittest.TestCase):
 def test_visible_answer_and_limits(self):
  text='<main><details><summary>Does it work?</summary><p>Checked 5 Nov; not tested.<sup>[1]</sup><span class="sr-only">external</span></p></details></main>'
  self.assertEqual(candidates(text),{'Does it work?':'Checked 5 Nov; not tested.'})
 def test_missing_answer_rejected(self):
  with patch('game_seo.settings',return_value={'pages':{'x/index.html':{'questions':['Missing?']}},'groups':[]}):
   with self.assertRaises(ValueError):edit(ROOT/'x/index.html','<html lang="en"><head><link rel="canonical" href="https://megabonk.org/x/"></head><body></body></html>')
 def test_safe_json_idempotency_and_unrelated_schema(self):
  text='<html lang="en"><head><link rel="canonical" href="https://megabonk.org/x/"><script type="application/ld+json">{"@type":"WebPage"}</script></head><body><h2>Safe?</h2><p>&lt;/script&gt; No guarantee.</p></body></html>'
  with patch('game_seo.settings',return_value={'pages':{'x/index.html':{'questions':['Safe?']}},'groups':[]}):
   actual=edit(ROOT/'x/index.html',text);self.assertEqual(edit(ROOT/'x/index.html',actual),actual);self.assertIn('\\u003c/script\\u003e',actual);self.assertIn('{"@type":"WebPage"}',actual)
 def test_outside_scope_unchanged(self):self.assertEqual(edit(ROOT/'unknown.html','test'),'test')
if __name__=='__main__':unittest.main()
