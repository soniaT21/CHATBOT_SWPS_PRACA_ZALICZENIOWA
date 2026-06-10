// Build entrypoint: the Flask app has no compiled output, so "build" just
// provisions the venv and installs dependencies. Cross-platform replacement
// for build.sh (works without bash on Windows).
import { ensureVenv } from "./scripts/venv.mjs";

ensureVenv();

console.log("api: dependencies installed");
