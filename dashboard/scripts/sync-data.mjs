// Copies the project's committed JSON data into dashboard/public/data/ so
// the React app can fetch it at runtime as static assets. Runs before both
// `dev` and `build` so the dashboard always reflects the current repo data
// without duplicating it as a second source of truth (public/data/ is
// gitignored -- regenerated every time, including by the weekly GitHub
// Actions build once that's wired up).
import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync, rmSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(__dirname, "..", "..");
const dataRoot = join(repoRoot, "data");
const outRoot = join(__dirname, "..", "public", "data");

rmSync(outRoot, { recursive: true, force: true });
mkdirSync(outRoot, { recursive: true });

function copyFile(src, destRelative) {
  const dest = join(outRoot, destRelative);
  mkdirSync(dirname(dest), { recursive: true });
  writeFileSync(dest, readFileSync(src));
}

function copyDirWithIndex(srcDir, destRelativeDir) {
  const outDir = join(outRoot, destRelativeDir);
  mkdirSync(outDir, { recursive: true });
  if (!existsSync(srcDir)) {
    writeFileSync(join(outDir, "index.json"), JSON.stringify([]));
    return;
  }
  const files = readdirSync(srcDir).filter((f) => f.endsWith(".json"));
  for (const f of files) {
    copyFile(join(srcDir, f), join(destRelativeDir, f));
  }
  writeFileSync(join(outDir, "index.json"), JSON.stringify(files.sort()));
}

copyFile(join(dataRoot, "squad", "liverpool_2026_27.json"), "squad.json");
copyFile(join(dataRoot, "manager_priors", "iraola_2026.json"), "manager_prior.json");
copyDirWithIndex(join(dataRoot, "player_profiles"), "player_profiles");
copyDirWithIndex(join(dataRoot, "fixtures"), "fixtures");
copyDirWithIndex(join(dataRoot, "posteriors"), "posteriors");

console.log("[sync-data] copied squad, manager prior, player_profiles, fixtures, posteriors into public/data/");
