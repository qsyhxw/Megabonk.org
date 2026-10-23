// Static successes keep their normal routing and headers. Pages' generated 404
// responses do not inherit _headers, so apply the same no-transform contract
// at the response boundary for this section's missing paths only.
export async function onRequest(context) {
  const response = await context.next();
  if (response.status !== 404) return response;

  const headers = new Headers(response.headers);
  headers.set('Cache-Control', 'public, max-age=0, must-revalidate, no-transform');
  const missing = new Response(response.body, {
    status: 404,
    statusText: 'Not Found',
    headers,
  });
  // Remove only the analytics beacon if it was inserted by the asset layer.
  // Bot/security scripts and all other response headers remain intact.
  return new HTMLRewriter()
    .on('script[src*="static.cloudflareinsights.com/beacon.min.js"]', {
      element(element) { element.remove(); },
    })
    .transform(missing);
}
