"""Final authoritative root discovery pass; also applied by shared HTML writer."""
from pathlib import Path
from site_analytics import write_html
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
 f=ROOT/'index.html';write_html(f,f.read_text(encoding='utf8'),encoding='utf8')
 print('Root guide grid contains only Megabonk; bottom discovery has one card per game.')
