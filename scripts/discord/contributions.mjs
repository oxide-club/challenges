import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import { createClient } from './client.mjs';
import { deliver } from './state.mjs';

export function selectProposals(files, kind) {
  const pattern =
    kind === 'challenge'
      ? /^\d{3}-[a-z0-9]+(?:-[a-z0-9]+)*$/
      : /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
  return [
    ...new Set(
      files.flatMap((file) => {
        const [id, name, extra] = file.filename.split('/');
        return file.status === 'added' &&
          name === 'index.md' &&
          extra === undefined &&
          !['docs', 'templates'].includes(id) &&
          pattern.test(id)
          ? [id]
          : [];
      }),
    ),
  ].sort();
}
export async function notifyContribution({ client, repository, pullRequest }) {
  const kind = {
    'oxide-club/challenges': 'challenge',
    'oxide-club/notes': 'note',
  }[repository];
  if (!kind) throw new Error('Unsupported contributions repository');
  if (!Number.isSafeInteger(pullRequest) || pullRequest < 1)
    throw new Error('Invalid PR number');
  const pr = await client.github(`/repos/${repository}/pulls/${pullRequest}`);
  if (pr.state !== 'open' || pr.draft || pr.base?.ref !== 'main') return;
  const files = await client.paginate(
    `/repos/${repository}/pulls/${pullRequest}/files`,
  );
  if (files.length !== pr.changed_files)
    throw new Error('Incomplete PR file list; retry against a stable revision');
  const ids = selectProposals(files, kind);
  if (!ids.length) return;
  const url = `https://github.com/${repository}/pull/${pullRequest}`;
  const label = kind === 'challenge' ? 'desafio' : 'nota';
  await deliver({
    client,
    repository,
    key: `pr:${pullRequest}`,
    url,
    payload: {
      content: `Proposta de ${label} pronta para revisão: ${url}`,
      embeds: [
        {
          title: String(pr.title).slice(0, 256),
          url,
          description:
            `Por ${pr.user.login}\n\nPropostas: ${ids.join(', ')}`.slice(
              0,
              2000,
            ),
        },
      ],
    },
  });
}
if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(process.argv[1]).href
) {
  try {
    const event = JSON.parse(
      await readFile(process.env.GITHUB_EVENT_PATH, 'utf8'),
    );
    await notifyContribution({
      client: createClient({
        token: process.env.GH_TOKEN,
        webhookUrl: process.env.DISCORD_CONTRIBUTIONS_WEBHOOK_URL,
      }),
      repository: process.env.GITHUB_REPOSITORY,
      pullRequest: event.number,
    });
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
