const branch = 'discord-state';
const empty = () => ({ version: 1, initialized: false, records: {}, revisions: {} });
const encode = value => Buffer.from(`${JSON.stringify(value, null, 2)}\n`).toString('base64');
export function validateState(state) {
  if (!state || state.version !== 1 || typeof state.initialized !== 'boolean' || !state.records || Array.isArray(state.records) || typeof state.records !== 'object' || !state.revisions || Array.isArray(state.revisions) || typeof state.revisions !== 'object') throw new Error('Invalid Discord state schema; refusing to reset history');
  for (const record of Object.values(state.records)) if (!record || typeof record !== 'object' || typeof record.url !== 'string' || (record.messageId !== undefined && !/^\d+$/.test(record.messageId))) throw new Error('Invalid Discord state record');
  return state;
}
export async function readState(client, repository) {
  let file;
  try { file = await client.github(`/repos/${repository}/contents/state.json?ref=${branch}`); }
  catch (error) { if (error.status === 404) return { state: empty(), sha: null }; throw error; }
  try {
    if (file.encoding !== 'base64' || !file.sha) throw new Error();
    return { state: validateState(JSON.parse(Buffer.from(file.content, 'base64').toString('utf8'))), sha: file.sha };
  } catch { throw new Error('Invalid Discord state file; refusing to reset history'); }
}
async function ensureBranch(client, repository) {
  const base = `/repos/${repository}/git`;
  try { await client.github(`${base}/ref/heads/${branch}`); return; }
  catch (error) { if (error.status !== 404) throw error; }
  const tree = await client.github(`${base}/trees`, { method: 'POST', body: { tree: [{ path: 'state.json', mode: '100644', type: 'blob', content: `${JSON.stringify(empty())}\n` }] } });
  const commit = await client.github(`${base}/commits`, { method: 'POST', body: { message: 'Initialize Discord notification state', tree: tree.sha, parents: [] } });
  try { await client.github(`${base}/refs`, { method: 'POST', body: { ref: `refs/heads/${branch}`, sha: commit.sha } }); }
  catch (error) { if (error.status !== 422) throw error; await client.github(`${base}/ref/heads/${branch}`); }
}
/** mutate must be synchronous and free of side effects: conflicts reapply it. */
export async function updateState(client, repository, mutate) {
  await ensureBranch(client, repository);
  for (let attempt = 0; attempt < 5; attempt++) {
    const { state, sha } = await readState(client, repository);
    if (!sha) throw new Error('State branch exists without state.json; repair it before sending');
    mutate(state); validateState(state);
    try {
      await client.github(`/repos/${repository}/contents/state.json`, { method: 'PUT', body: { branch, sha, message: 'Record Discord notification state', content: encode(state) } });
      return state;
    } catch (error) { if (![409, 422].includes(error.status) || attempt === 4) throw error; }
  }
}
/** Reserve before POST; a crash or ambiguous response requires explicit recovery. */
export async function deliver({ client, repository, key, url, payload }) {
  const { state } = await readState(client, repository);
  if (state.records[key]) {
    if (state.records[key].pending) throw new Error(`Pending delivery ${key}; reconcile before retrying.`);
    return;
  }
  await updateState(client, repository, current => {
    if (current.records[key]) throw new Error(`Delivery ${key} already reserved; retry after checking state.`);
    current.records[key] = { url, pending: true };
  });
  const message = await client.send(payload);
  await updateState(client, repository, current => { current.records[key] = { url, messageId: message.id }; });
}
