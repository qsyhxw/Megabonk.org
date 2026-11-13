/* Click-to-load YouTube player (v3.21). No request to YouTube until the visitor clicks. */
document.addEventListener('click', function (e) {
  var b = e.target.closest && e.target.closest('.yt-facade');
  if (!b) return;
  var f = document.createElement('iframe');
  var start = parseInt(b.getAttribute('data-start') || '0', 10);
  f.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(b.getAttribute('data-yt')) +
    '?autoplay=1&rel=0&playsinline=1' + (start ? '&start=' + start : '');
  f.title = (b.getAttribute('aria-label') || 'YouTube video').replace(/^Play video: /, '');
  f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
  f.referrerPolicy = 'strict-origin-when-cross-origin';
  f.allowFullscreen = true;
  f.className = 'yt-frame';
  b.replaceWith(f);
  f.focus();
});
