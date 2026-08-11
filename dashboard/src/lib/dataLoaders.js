const BASE = import.meta.env.BASE_URL;

async function getJson(path) {
  const res = await fetch(`${BASE}data/${path}`);
  if (!res.ok) throw new Error(`Failed to load ${path}: ${res.status}`);
  return res.json();
}

export async function loadSquad() {
  const data = await getJson('squad.json');
  return data.players ?? [];
}

export async function loadSquadMeta() {
  return getJson('squad.json');
}

export async function loadManagerPrior() {
  return getJson('manager_prior.json');
}

async function loadIndexedCollection(dir) {
  const index = await getJson(`${dir}/index.json`);
  const items = await Promise.all(index.map((file) => getJson(`${dir}/${file}`)));
  return items;
}

export async function loadPlayerProfiles() {
  return loadIndexedCollection('player_profiles');
}

export async function loadFixtures() {
  return loadIndexedCollection('fixtures');
}

export async function loadPosteriors() {
  return loadIndexedCollection('posteriors');
}
