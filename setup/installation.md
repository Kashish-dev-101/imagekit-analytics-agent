# Setup Guide

One-time setup. Once done, works across all Claude Code projects.

---

## What You Need

- Node.js **v20.19 or newer**
- VS Code (any recent version)
- Claude Code — VS Code extension + CLI
- Python 3 (for the data extractor)

No browser or MCP setup needed — this agent works entirely from files.

The URL/domain/IP skills (`/url-check`, `/ik-debug`, `/origin-vendor`, etc.) use `curl` and `dig`, which ship with macOS. No extra install needed.

---

## Step 1 — Install Node.js

*Claude Code runs on Node.js — this needs to be installed before anything else.*

Node.js must be installed before Claude Code. Check if you already have it:

```bash
node --version
```

If the version is v20.19 or newer, skip to Step 2.

### Install on macOS

**Option A — Homebrew (recommended if you have Homebrew):**

```bash
brew install node@20
```

**Option B — Direct download:**

Go to [nodejs.org/en/download](https://nodejs.org/en/download) and download the **macOS LTS installer** (.pkg file). Run it and follow the prompts.

After installing, verify:

```bash
node --version
npm --version
```

Both commands should return a version number.

---

## Step 2 — Install VS Code

*VS Code is the editor where Claude Code lives — you'll run the agent through a chat panel inside it.*

Download and install from [code.visualstudio.com](https://code.visualstudio.com/).

---

## Step 3 — Install the Claude Code VS Code Extension

*This adds the Claude Code chat panel to VS Code — it's where you'll type commands and see the analysis run.*

Open VS Code → Extensions panel (⇧⌘X) → search **Claude Code** → Install.

Direct link: [marketplace.visualstudio.com/items?itemName=anthropic.claude-code](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code)

---

## Step 4 — Install the Claude Code CLI

*The CLI is what actually powers Claude Code under the hood. The VS Code extension and CLI work together.*

```bash
npm install -g @anthropic-ai/claude-code
```

Verify it installed:

```bash
claude --version
```

### Sign in

Run `claude` in your terminal — it will open a browser window to authenticate with your Anthropic account on first run.

---

## Step 5 — Set up Python 3 and dependencies

*Before analysis runs, the agent compresses the JSON into a compact format using a small Python script. This step installs what that script needs.*

The data extractor (`agent/extract.py`) requires Python 3 and one library. Do both:

**Check Python 3:**

```bash
python3 --version
```

macOS ships with Python 3 — if the command returns a version, you're good. If not, install via Homebrew:

```bash
brew install python3
```

**Install the required library:**

```bash
pip3 install -r requirements.txt
```

This installs `device-detector`, which the extractor uses to classify User-Agent strings (browser, native app, bot, etc.) before analysis.

Verify it installed:

```bash
python3 -c "from device_detector import DeviceDetector; print('OK')"
```

You should see `OK`. If you see an error, re-run `pip3 install -r requirements.txt`.

---

## Step 6 — Clone the repo and open in VS Code

*This downloads the project to your computer.*

```bash
git clone https://github.com/Kashish-dev-101/imagekit-analytics-agent.git
cd imagekit-analytics-agent
code .
```

Or open the folder in VS Code manually via **File → Open Folder**.

---

## You're ready

Open Claude Code in the sidebar and follow the **How to Use** steps in `README.md`.
