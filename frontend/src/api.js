const OFFLINE_MESSAGE =
  "Can't reach the analysis server. Start the backend (python main.py in the backend folder) and try again.";

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(path, options);
  } catch (err) {
    if (err.name === 'AbortError') throw err;
    throw new Error(OFFLINE_MESSAGE);
  }

  let data = null;
  try {
    data = await res.json();
  } catch {
    // Non-JSON response (e.g. dev proxy error page)
  }

  if (!res.ok) {
    if (!data && res.status >= 500) throw new Error(OFFLINE_MESSAGE);
    const detail = data?.detail;
    if (typeof detail === 'string') throw new Error(detail);
    if (Array.isArray(detail)) throw new Error(detail.map((d) => d.msg).join('; '));
    throw new Error(`Something went wrong (error ${res.status}). Please try again.`);
  }
  return data;
}

export function getJSON(path, options) {
  return request(path, options);
}

export function postJSON(path, body, options = {}) {
  return request(path, {
    ...options,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
}
