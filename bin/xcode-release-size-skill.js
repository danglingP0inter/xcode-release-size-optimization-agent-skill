#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const repoRoot = path.resolve(__dirname, "..");
const packageJson = JSON.parse(
  fs.readFileSync(path.join(repoRoot, "package.json"), "utf8"),
);
const python = process.env.PYTHON || "python3";

const commands = {
  measure: {
    script: "measure_release.py",
    description: "Collect a Release build size baseline and optional IPA export.",
  },
  report: {
    script: "render_report.py",
    description: "Render the Markdown size optimization report from JSON artifacts.",
  },
  compare: {
    script: "compare_runs.py",
    description: "Compare baseline and post-change size measurements.",
  },
  fix: {
    script: "apply_low_risk_size_fixes.py",
    description: "Apply approved low-risk Release-only size setting changes.",
  },
  "analyze-build-settings": {
    script: "analyze_build_settings.py",
    description: "Inspect Release build settings relevant to shipped size.",
  },
  "analyze-macho": {
    script: "analyze_macho.py",
    description: "Inspect Mach-O binaries and embedded framework footprint.",
  },
  "analyze-resources": {
    script: "analyze_resources.py",
    description: "Inspect bundled resources, assets, and localization payloads.",
  },
  "analyze-swiftpm": {
    script: "analyze_swiftpm.py",
    description: "Inspect SwiftPM package contributions to shipped size.",
  },
};

function printHelp(exitCode = 0) {
  const rows = Object.entries(commands)
    .map(([name, config]) => `  ${name.padEnd(24)} ${config.description}`)
    .join("\n");

  console.log(`Xcode Release Size Optimization Agent Skill CLI v${packageJson.version}

Usage:
  xcode-release-size-skill <command> [args...]
  xcode-release-size-skill help <command>
  xcode-release-size-skill --help
  xcode-release-size-skill --version

Commands:
${rows}

Examples:
  xcode-release-size-skill measure --workspace-root /path/to/app --project MyApp.xcodeproj --scheme MyApp --configuration Release --export-ipa
  xcode-release-size-skill report --artifacts-dir /path/to/app/.size-analysis
  xcode-release-size-skill fix --pbxproj /path/to/project.pbxproj --approved-json /path/to/approved.json

Environment:
  PYTHON    Override the Python executable used to run the bundled scripts.
`);
  process.exit(exitCode);
}

const rawArgs = process.argv.slice(2);
if (rawArgs.length === 0 || rawArgs[0] === "--help" || rawArgs[0] === "-h") {
  printHelp(0);
}

if (rawArgs[0] === "--version" || rawArgs[0] === "-v" || rawArgs[0] === "version") {
  console.log(packageJson.version);
  process.exit(0);
}

let command = rawArgs[0];
let scriptArgs = rawArgs.slice(1);

if (command === "help") {
  if (scriptArgs.length === 0) {
    printHelp(0);
  }
  command = scriptArgs[0];
  scriptArgs = ["--help"];
}

const target = commands[command];
if (!target) {
  console.error(`Unknown command: ${command}`);
  printHelp(1);
}

const scriptPath = path.join(repoRoot, "scripts", target.script);
if (!fs.existsSync(scriptPath)) {
  console.error(`Missing script: ${scriptPath}`);
  process.exit(1);
}

const result = spawnSync(python, [scriptPath, ...scriptArgs], {
  cwd: process.cwd(),
  stdio: "inherit",
  env: process.env,
});

if (result.error) {
  if (result.error.code === "ENOENT") {
    console.error(`Unable to find Python executable: ${python}`);
  } else {
    console.error(result.error.message);
  }
  process.exit(1);
}

process.exit(result.status === null ? 1 : result.status);
