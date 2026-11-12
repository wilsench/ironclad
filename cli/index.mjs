#!/usr/bin/env node
// Entry point for `npx github:wilsench/ironclad`.
//
// Node is only a delivery mechanism here — npm runs this file, which locates the
// bash installer that already sits next to it in the package and hands over. All
// the real logic stays in install.sh so `curl | bash` and `npx` run identical code.
// Two installers that drift apart is the exact class of bug this tool exists to
// prevent.

import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
// index.mjs lives in cli/, install.sh in the package root.
const installer = join(here, "..", "install.sh");

if (!existsSync(installer)) {
  console.error("ironclad: install.sh is missing from this package.");
  console.error("This usually means npm pack ignored it — check the files list in package.json.");
  process.exit(1);
}

const hasBash = spawnSync("bash", ["-c", "true"], { stdio: "ignore" });
if (hasBash.error || hasBash.status !== 0) {
  console.error("ironclad: bash is required. On Windows use WSL or Git Bash.");
  process.exit(3);
}

// Everything after the package name is passed straight through, so
// `npx github:wilsench/ironclad --uninstall` and `--dry-run` work unchanged.
const result = spawnSync("bash", [installer, ...process.argv.slice(2)], {
  stdio: "inherit",
  env: process.env,
});

if (result.error) {
  console.error(`ironclad: could not run the installer: ${result.error.message}`);
  process.exit(1);
}

process.exit(result.status ?? 1);
