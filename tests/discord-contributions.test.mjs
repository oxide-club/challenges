import { test } from 'node:test';
import assert from 'node:assert/strict';
import { selectProposals, notifyContribution } from '../scripts/discord/contributions.mjs';
import { memoryClient } from './helpers/discord-api.mjs';
const repository = 'oxide-club/notes';
const proposal = { number: 12, state: 'open', draft: false, title: 'Uma nota @everyone', user: { login: 'alice' }, base: { ref: 'main' }, head: { repo: { full_name: 'alice/notes' } }, changed_files: 1 };
const files = [{ filename: 'memoria/index.md', status: 'added' }];
test('selects only new canonical entries and ignores docs, edits and renames', () => {
  const paths = ['memoria/index.md', 'docs/index.md', 'templates/index.md', 'memoria/assets/a.png', 'index.md', '../index.md'];
  assert.deepEqual(selectProposals(paths.map(filename => ({ filename, status: 'added' })), 'note'), ['memoria']);
  assert.deepEqual(selectProposals([{ filename: 'memoria/index.md', status: 'renamed' }, { filename: 'outra/index.md', status: 'modified' }], 'note'), []);
  assert.deepEqual(selectProposals([{ filename: '004-http/index.md', status: 'added' }, { filename: 'http/index.md', status: 'added' }], 'challenge'), ['004-http']);
});
test('fork PR message points to GitHub and subsequent updates do not repeat it', async () => {
  const api = memoryClient({ pullRequest: proposal, files });
  await notifyContribution({ client: api.client, repository, pullRequest: 12 });
  assert.equal(api.messages.length, 1);
  assert.equal(api.messages[0].embeds[0].url, 'https://github.com/oxide-club/notes/pull/12');
  assert.match(api.messages[0].content, /https:\/\/github.com\/oxide-club\/notes\/pull\/12/);
  assert.equal(api.state().records['pr:12'].messageId, '101');
  await notifyContribution({ client: api.client, repository, pullRequest: 12 });
  assert.equal(api.messages.length, 1);
});
test('draft, closed, other target and existing-content PRs are silent', async () => {
  for (const patch of [{ draft: true }, { state: 'closed' }, { base: { ref: 'other' } }]) {
    const api = memoryClient({ pullRequest: { ...proposal, ...patch }, files });
    await notifyContribution({ client: api.client, repository, pullRequest: 12 }); assert.equal(api.messages.length, 0);
  }
  const api = memoryClient({ pullRequest: { ...proposal, changed_files: 1 }, files: [{ filename: 'memoria/index.md', status: 'modified' }] });
  await notifyContribution({ client: api.client, repository, pullRequest: 12 }); assert.equal(api.messages.length, 0);
});
test('later update adding multiple proposals produces one bounded message', async () => {
  const api = memoryClient({ pullRequest: { ...proposal, title: 'x'.repeat(1000), changed_files: 2 }, files: [...files, { filename: 'outro/index.md', status: 'added' }] });
  await notifyContribution({ client: api.client, repository, pullRequest: 12 });
  assert.equal(api.messages.length, 1); assert.ok(api.messages[0].embeds[0].title.length <= 256);
  assert.match(api.messages[0].embeds[0].description, /memoria/); assert.match(api.messages[0].embeds[0].description, /outro/);
});
test('incomplete file list fails and ambiguous sends remain pending', async () => {
  const api = memoryClient({ pullRequest: { ...proposal, changed_files: 2 }, files });
  await assert.rejects(notifyContribution({ client: api.client, repository, pullRequest: 12 }), /Incomplete/);
  const broken = memoryClient({ pullRequest: proposal, files, sendError: new Error('Lost confirmation') });
  await assert.rejects(notifyContribution({ client: broken.client, repository, pullRequest: 12 }));
  await assert.rejects(notifyContribution({ client: broken.client, repository, pullRequest: 12 }), /Pending/);
  assert.equal(broken.messages.length, 1);
  await assert.rejects(notifyContribution({ client: api.client, repository: 'evil/notes', pullRequest: 12 }), /repository/);
});
