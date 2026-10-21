export function memoryClient({
  initialized = true,
  records = {},
  revisions = {},
  pullRequest,
  files = [],
  sendError,
} = {}) {
  let state = {
    version: 1,
    initialized,
    records: structuredClone(records),
    revisions,
  };
  let sha = 1;
  const messages = [];
  const client = {
    async github(path, options = {}) {
      if (path.includes('/contents/state.json')) {
        if (options.method === 'PUT') {
          if (options.body.sha !== String(sha))
            throw Object.assign(new Error('Conflict'), { status: 409 });
          state = JSON.parse(
            Buffer.from(options.body.content, 'base64').toString(),
          );
          sha++;
          return {};
        }
        return {
          encoding: 'base64',
          sha: String(sha),
          content: Buffer.from(JSON.stringify(state)).toString('base64'),
        };
      }
      if (path.endsWith('/git/ref/heads/discord-state'))
        return { object: { sha: 'a'.repeat(40) } };
      if (/\/pulls\/\d+$/.test(path)) return pullRequest;
      throw new Error(`Unexpected fixture API: ${path}`);
    },
    async paginate(path) {
      if (path.endsWith('/files')) return files;
      throw new Error('Unexpected fixture pagination');
    },
    async send(payload) {
      messages.push(payload);
      if (sendError) throw sendError;
      return { id: String(100 + messages.length) };
    },
  };
  return { client, messages, state: () => structuredClone(state) };
}
