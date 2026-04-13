# Setup Guide

One-time setup. Once done, works across all Claude Code projects.

---

## What You Need

- Node.js **v20.19 or newer**
- VS Code (any recent version)
- Claude Code — VS Code extension + CLI
- Python 3 (for the data extractor)

No browser or MCP setup needed — this agent works entirely from files.

---

## Step 1 — Install Node.js

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

Download and install from [code.visualstudio.com](https://code.visualstudio.com/).

---

## Step 3 — Install the Claude Code VS Code Extension

Open VS Code → Extensions panel (⇧⌘X) → search **Claude Code** → Install.

Direct link: [marketplace.visualstudio.com/items?itemName=anthropic.claude-code](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code)

---

## Step 4 — Install the Claude Code CLI

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

## Step 5 — Check Python 3

The data extractor (`input/extract.py`) requires Python 3. Check if it's installed:

```bash
python3 --version
```

macOS ships with Python 3 — if the command returns a version, you're good. If not, install it via Homebrew:

```bash
brew install python3
```

---

## Step 6 — Clone the repo and open in VS Code

```bash
git clone https://github.com/Kashish-dev-101/imagekit-analytics-agent.git
cd imagekit-analytics-agent
code .
```

Or open the folder in VS Code manually via **File → Open Folder**.

---

## You're ready

Open Claude Code in the sidebar and follow the **How to Use** steps in `README.md`.
