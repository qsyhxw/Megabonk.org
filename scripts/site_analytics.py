"""User-authorized site-wide Umami tag, shared by HTML generators."""
from pathlib import Path
import re

TAG = '<script defer src="https://umami-nine-rust.vercel.app/script.js" data-website-id="be597e21-a994-45fc-8c3c-5893c6cece58"></script>'
NOTICE = '<h2 id="umami-analytics">Site-wide Umami analytics</h2><p>Updated 3 November 2026. All Megabonk.org pages, including guide sections, privacy and contact pages, and error pages, load Umami from umami-nine-rust.vercel.app to measure website usage. Your browser connects to that service and sends page-view information such as the page URL, referrer and browser/device details. This site-wide service also applies to sections described below as adding no separate analytics tag.</p>'


def inject(html):
    if TAG in html:
        return html
    if 'umami-nine-rust.vercel.app/script.js' in html:
        raise ValueError('Unexpected Umami tag; review instead of duplicating')
    if not re.search(r'</head\s*>', html, re.I):
        raise ValueError('HTML document has no closing head')
    return re.sub(r'</head\s*>', lambda m: TAG + '\n' + m[0], html, count=1, flags=re.I)


def write_html(path, text, **kwargs):
    path = Path(path)
    if path.suffix.lower() in ('.html', '.htm'):
        from game_sections import normalize
        text = normalize(path, text)
        from remaining_editorial import edit, edit_captions
        text = edit(path, text)
        text = edit_captions(path, text)
        text = inject(text)
        if (path.name == 'privacy-policy.html' or
                path.as_posix().endswith('/privacy/index.html')):
            if 'id="umami-analytics"' not in text:
                text = text.replace('</body>', NOTICE + '\n</body>', 1)
        from game_seo import edit as edit_seo
        text = edit_seo(path, text)
        # v3.20 presentation (SOP 00 §1.4/§4) for every generated page except trust/404.
        if not re.search(r'(?:^|/)(?:about|contact|privacy|privacy-policy|terms)(?:/|\.html|$)|404\.html$', path.as_posix()):
            from v320_present import transform as _v320
            text = _v320(text, 'megabonk.org')
            if 'data-v320=' not in text:
                text = re.sub(r'<body(?=[\s>])', '<body data-v320="1"', text, count=1)
            # Re-apply the SEO editor so its own idempotence check still holds.
            text = edit_seo(path, text)
    return path.write_text(text, **kwargs)
