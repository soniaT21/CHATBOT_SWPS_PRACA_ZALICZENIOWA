// Dev entrypoint: provision the venv, then run the Flask dev server on port 5001.
// Cross-platform replacement for dev.sh (works without bash on Windows).
import { spawn } from "node:child_process";
import { apiDir, ensureVenv, venvPython } from "./scripts/venv.mjs";

ensureVenv();

const server = spawn(
  venvPython(),
  ["-m", "flask", "--app", "app", "run", "--port", "5001", "--debug"],
  { cwd: apiDir, stdio: "inherit" },
);

// Relay termination signals so Ctrl-C / Turbo shutdown stops Flask cleanly.
for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => server.kill(signal));
}

server.on("exit", (code, signal) => {
  if (signal) process.kill(process.pid, signal);
  else process.exit(code ?? 0);
});
