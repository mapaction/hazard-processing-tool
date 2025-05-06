# Hazard Processing Tool - WSL & Linux Setup Guide

This is a short guide to help run the hazard-processing-tool
on a Windows machine using WSL (Windows Subsystem for Linux), or on any Linux computer.

## Why use WSL?

WSL lets you run Linux tools on a Windows PC. It works
the same as running the project on a Linux or Mac machine,
including using commands like `make`, `poetry`, and `streamlit`.

---

## Step-by-step setup (WSL)

### 1. Install WSL and Ubuntu

Open PowerShell as Admin and run:

```powershell
wsl --install
```

If it gets stuck, open the **Microsoft Store**, search for **Ubuntu**,
and install it manually.

Once Ubuntu is installed, launch it from the Start menu.

---

### 2. Set up Ubuntu

Inside the Ubuntu terminal and after creating a user, run:

```bash
sudo apt update
sudo apt install python3 python3-pip make curl git
```

---

### 3. Install Poetry

Run this command to install Poetry:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Then add Poetry to your terminal path (so the `poetry` command works):

```bash
export PATH="$HOME/.local/bin:$PATH"
```

You can check if it worked with:

```bash
poetry --version
```

If it works, make the path permanent by adding it to your `~/.bashrc`:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

### 4. Clone the project and install dependencies

Now clone the repo and install everything:

```bash
git clone https://github.com/mapaction/hazard-processing-tool.git
cd hazard-processing-tool
make .venv
make hooks
```

---

### 5. Set environment variables for local mode

If you're only running locally (no cloud), create this file:

```bash
nano ~/.hazard_tool_rc
```

Paste this in:

```bash
export USE_LOCAL=true
export S3_BUCKET=dummy-bucket
export AWS_ACCESS_KEY_ID=dummy
export AWS_SECRET_ACCESS_KEY=dummy
export AWS_DEFAULT_REGION=eu-west-2
```

Then run:

```bash
source ~/.hazard_tool_rc
```

---

### 6. Run the tool

Run the tool locally with:

```bash
make local_etl
```

To open the Streamlit web app:

```bash
make app
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

### Notes for Linux users

If you're on Linux and `poetry` is not found after install, just run:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

And then optionally add it to `~/.bashrc` so it stays after reboot:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```
