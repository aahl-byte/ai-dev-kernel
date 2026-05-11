import { execFileSync } from "node:child_process";
import { resolve } from "node:path";

const args = process.argv.slice(2);
const prompt = args.length ? `/dk ${args.join(" ")}` : "/dk";
const dir = resolve(import.meta.dirname, "../..");
const term = process.env.TERM_PROGRAM ?? "";

const shellCmd = `cd '${dir}' && claude '${prompt}'`;

switch (term) {
  case "Apple_Terminal": {
    execFileSync("osascript", [
      "-e",
      [
        'tell application "Terminal"',
        `  do script "${shellCmd}"`,
        "  activate",
        "end tell",
      ].join("\n"),
    ]);
    break;
  }

  case "iTerm.app": {
    execFileSync("osascript", [
      "-e",
      [
        'tell application "iTerm2"',
        "  create window with default profile",
        "  tell current session of current window",
        `    write text "${shellCmd}"`,
        "  end tell",
        "end tell",
      ].join("\n"),
    ]);
    break;
  }

  case "WezTerm": {
    execFileSync("wezterm", ["cli", "spawn", "--", "bash", "-c", shellCmd]);
    break;
  }

  default:
    console.error(`Unsupported terminal: ${term || "unknown"}`);
    console.error(`Run manually in a new terminal:\n\n  ${shellCmd}\n`);
    process.exit(1);
}

console.log(`Launched: ${prompt}`);
