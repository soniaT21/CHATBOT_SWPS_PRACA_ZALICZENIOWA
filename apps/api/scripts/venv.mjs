// Cross-platform helpers for provisioning the Python virtualenv used by the api.
//
// Replaces the bash logic from dev.sh/build.sh so the scripts work on Windows,
// macOS and Linux without bash. Only the python interpreter path differs per OS;
// everything else runs through `python -m ...`.
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const isWindows = process.platform === "win32";

// apps/api directory, resolved from this file's location (scripts/ -> api/).
// fileURLToPath keeps this working on Node 18 (import.meta.dirname is 20.11+).
export const apiDir = dirname(dirname(fileURLToPath(import.meta.url)));

const venvDir = join(apiDir, ".venv");

// Path to the virtualenv's python interpreter for the current platform.
export function venvPython() {
  return isWindows
    ? join(venvDir, "Scripts", "python.exe")
    : join(venvDir, "bin", "python");
}

// Find a usable system python to create the venv. Probes common command names
// (Windows lacks `python3`; the `py` launcher is the most reliable there).
function findSystemPython() {
  const candidates = isWindows
    ? ["py", "python", "python3"]
    : ["python3", "python"];
  for (const cmd of candidates) {
    const result = spawnSync(cmd, ["--version"], { stdio: "ignore" });
    if (!result.error && result.status === 0) return cmd;
  }
  console.error(
    "api: Python 3.9+ not found on PATH. Install Python and ensure " +
      `one of [${candidates.join(", ")}] runs in your terminal.`,
  );
  process.exit(1);
}

// Run a command in apiDir with inherited stdio; exit on failure (mirrors `set -e`).
function run(cmd, args) {
  const result = spawnSync(cmd, args, { cwd: apiDir, stdio: "inherit" });
  if (result.error) {
    console.error(`api: failed to run ${cmd}: ${result.error.message}`);
    process.exit(1);
  }
  if (result.status !== 0) process.exit(result.status ?? 1);
}

// Create .venv if missing, then install requirements. Idempotent.
export function ensureVenv() {
  if (!existsSync(venvDir)) {
    run(findSystemPython(), ["-m", "venv", ".venv"]);
  }
  run(venvPython(), ["-m", "pip", "install", "-q", "-r", "requirements.txt"]);
}
