// Keep versioned build sources and machine inventories out of public assets.
// _routes.json invokes this only for the explicit source paths and the already
// existing PokeBonk function scope; ordinary static HTML keeps its static route.
export async function onRequest(context) {
  const url = new URL(context.request.url);
  if (/^\/(scripts|config)(\/|$)/.test(url.pathname) || url.pathname.endsWith('.py')) {
    const page = await context.env.ASSETS.fetch(new Request(new URL('/404.html', url)));
    const headers = new Headers(page.headers);
    headers.set('Content-Type', 'text/html; charset=utf-8');
    headers.set('X-Robots-Tag', 'noindex, follow');
    headers.delete('Content-Disposition');
    return new Response(page.body, { status: 404, statusText: 'Not Found', headers });
  }
  return context.next();
}
