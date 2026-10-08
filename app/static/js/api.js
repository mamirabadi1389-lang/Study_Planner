const Api = (() => {
  const call = async (method, url, body) => {
    const res = await fetch(`/api${url}`, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || 'خطای سرور');
    return data;
  };

  return {
    get: (url) => call('GET', url),
    post: (url, body = {}) => call('POST', url, body),
    put: (url, body) => call('PUT', url, body),
    patch: (url, body) => call('PATCH', url, body),
    del: (url) => call('DELETE', url),
  };
})();