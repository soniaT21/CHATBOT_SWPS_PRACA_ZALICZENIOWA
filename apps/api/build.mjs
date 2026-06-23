// Skrypt produkcyjny backendu (wieloplatformowy).
// Zapewnia środowisko wirtualne i zainstalowane zależności.
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const isWin = process.platform === "win32";
const venvDir = join(__dirname, ".venv");
const pyBin = isWin
  ? join(venvDir, "Scripts", "python.exe")
  : join(venvDir, "bin", "python");

function run(cmd, args) {
  return spawnSync(cmd, args, { stdio: "inherit", cwd: __dirname });
}

function findBasePython() {
  const candidates = isWin ? ["py", "python", "python3"] : ["python3", "python"];
  for (const c of candidates) {
    const r = spawnSync(c, ["--version"], { stdio: "ignore" });
    if (r.status === 0) return c;
  }
  console.error("Nie znaleziono Pythona 3.9+.");
  process.exit(1);
}

if (!existsSync(pyBin)) {
  const basePy = findBasePython();
  console.log("Tworzę środowisko wirtualne (.venv)...");
  run(basePy, ["-m", "venv", ".venv"]);
  run(pyBin, ["-m", "pip", "install", "--upgrade", "pip"]);
  run(pyBin, ["-m", "pip", "install", "-r", "requirements.txt"]);
}

console.log("Backend gotowy (zależności zainstalowane).");
