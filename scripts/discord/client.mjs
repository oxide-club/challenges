/** External requests are bounded, never redirect credentials, and never echo response bodies. */
export function createClient({
  fetch = globalThis.fetch,
  sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
  token,
  webhookUrl,
} = {}) {
  async function request(url, options, label) {
    for (let attempt = 0; attempt < 3; attempt++) {
      let response;
      try {
        response = await fetch(url, {
          ...options,
          redirect: 'error',
          signal: AbortSignal.timeout(20000),
        });
      } catch {
        throw new Error(
          `${label} request failed; reconcile any pending delivery before retrying.`,
        );
      }
      if (response.status === 429 && attempt < 2) {
        const data = await response.json().catch(() => ({}));
        const seconds = Number(
          data.retry_after ?? response.headers.get('retry-after'),
        );
        if (Number.isFinite(seconds) && seconds > 0 && seconds <= 60) {
          await sleep(seconds * 1000);
          continue;
        }
      }
      if (!response.ok)
        throw Object.assign(new Error(`${label} HTTP ${response.status}`), {
          status: response.status,
        });
      try {
        return await response.json();
      } catch {
        throw new Error(`${label} invalid JSON response`);
      }
    }
  }
  async function github(path, { method = 'GET', body } = {}) {
    if (
      !/^\/repos\/oxide-club\/[a-z0-9.-]+\//.test(path) ||
      path.includes('..') ||
      path.includes('\\') ||
      /[\r\n]/.test(path)
    )
      throw new Error('Invalid GitHub path');
    return request(
      `https://api.github.com${path}`,
      {
        method,
        headers: {
          Accept: 'application/vnd.github+json',
          Authorization: `Bearer ${token}`,
          'X-GitHub-Api-Version': '2026-03-10',
          'Content-Type': 'application/json',
        },
        ...(body === undefined ? {} : { body: JSON.stringify(body) }),
      },
      'GitHub',
    );
  }
  async function paginate(path, field) {
    const values = [];
    for (let page = 1; page <= 31; page++) {
      const response = await github(
        `${path}${path.includes('?') ? '&' : '?'}per_page=100&page=${page}`,
      );
      const data = field ? response[field] : response;
      if (!Array.isArray(data)) throw new Error('Invalid GitHub list response');
      values.push(...data);
      if (data.length < 100) return values;
    }
    throw new Error('GitHub pagination exceeded safe limit');
  }
  async function send(payload) {
    let url;
    try {
      url = new URL(webhookUrl);
    } catch {
      throw new Error('Configure a valid Discord webhook');
    }
    if (
      url.protocol !== 'https:' ||
      url.hostname !== 'discord.com' ||
      url.port ||
      url.username ||
      url.password ||
      !/^\/api\/webhooks\/\d+\/[A-Za-z0-9_-]+$/.test(url.pathname)
    )
      throw new Error('Invalid Discord webhook URL');
    url.search = '?wait=true';
    const result = await request(
      url.href,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...payload, allowed_mentions: { parse: [] } }),
      },
      'Discord',
    );
    if (!/^\d+$/.test(result?.id))
      throw new Error(
        'Discord did not confirm a message ID; reconcile pending delivery.',
      );
    return { id: result.id };
  }
  return { github, paginate, send };
}
