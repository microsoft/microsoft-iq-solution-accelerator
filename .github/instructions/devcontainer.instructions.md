---
description: "Use when editing files under .devcontainer/ (devcontainer.json, Dockerfile, post-create.sh, setup_env.sh). Covers the post-create flow, configuration source-of-truth, and documentation sync with .devcontainer/README.md."
applyTo: ".devcontainer/**"
---

# Dev container — configuration and documentation sync

The [`.devcontainer/`](../../.devcontainer/) folder defines the reproducible Linux environment used by VS Code Dev Containers and GitHub Codespaces. Every change in this folder must keep the on-disk configuration and [`./.devcontainer/README.md`](../../.devcontainer/README.md) consistent.

## Files in scope

| File | Role |
|---|---|
| [`.devcontainer/devcontainer.json`](../../.devcontainer/devcontainer.json) | Manifest: base image build, [Dev Container Features](https://containers.dev/features), VS Code extensions and settings, mounts, `forwardPorts`, `hostRequirements`, `postCreateCommand`. |
| [`.devcontainer/Dockerfile`](../../.devcontainer/Dockerfile) | Base image (`mcr.microsoft.com/devcontainers/python:3.11-bullseye`) plus minimal patches (currently removes the expired Yarn apt repo). |
| [`.devcontainer/post-create.sh`](../../.devcontainer/post-create.sh) | Runs as `vscode` after the container is built. Installs Python project dependencies from [`requirements.txt`](../../requirements.txt) and [`src/fabric/datagen/requirements.txt`](../../src/fabric/datagen/requirements.txt), the optional sibling `../fabric-launcher`, dev tooling (black/flake8/pytest/mypy/bandit/jupyter), shell aliases, and fixes script permissions / CRLF line endings under [`infra/scripts/`](../../infra/scripts/). |
| [`.devcontainer/setup_env.sh`](../../.devcontainer/setup_env.sh) | Runs after `post-create.sh`. Privileged block (under `sudo bash <<EOF` heredoc) installs `msodbcsql18` + `unixodbc` + `unixodbc-dev` from the Microsoft Debian repo. Unprivileged block refreshes the git tree (`fetch`/`pull` as best-effort) and `chmod +x` on helper scripts that exist. |
| [`.devcontainer/README.md`](../../.devcontainer/README.md) | User-facing documentation for the dev container. Must mirror the on-disk configuration. |
| [`.devcontainer/.dockerignore`](../../.devcontainer/.dockerignore) | Files excluded from the Docker build context. |

## Hard rules

### `postCreateCommand` invocation

The `postCreateCommand` in [`devcontainer.json`](../../.devcontainer/devcontainer.json) **must** invoke each shell script via `bash <script>` (not `exec <script>` or just `<script>`). Codespaces clones the repository without preserving the executable bit, so an `exec`-style invocation fails with `Permission denied` (exit 126). Current value:

```
bash .devcontainer/post-create.sh && bash .devcontainer/setup_env.sh
```

### `setup_env.sh` privilege handling

Do not re-exec the script under `sudo` (e.g. `exec sudo bash "$0" "$@"`). That pattern would also require the `+x` bit on the script and break under Codespaces. Run only the privileged block under `sudo bash <<'EOF' ... EOF`, then return to the `vscode` user automatically when the heredoc exits.

### `chmod +x` loops

Only `chmod +x` files that exist on disk. Inside `set -e` / `set -u`, a missing file aborts the entire script. Use a guarded loop:

```bash
for script in ./infra/scripts/foo.sh ./infra/scripts/bar.sh; do
    [ -f "$script" ] && chmod +x "$script"
done
```

### VS Code extension IDs

Every ID in `customizations.vscode.extensions` **must** resolve on the [VS Code Marketplace](https://marketplace.visualstudio.com/vscode). Common pitfalls:

- **Azure CLI Tools** is published as `ms-vscode.azurecli`, *not* `ms-azuretools.vscode-azurecli`.
- **JSON support is built into VS Code.** There is no `ms-vscode.vscode-json` extension; do not add one.
- When adding a new extension, fetch the marketplace page first and confirm the `Unique Identifier`.

### Line endings

All shell scripts under `.devcontainer/` must use `LF` (Unix) line endings. CRLF breaks bash shebangs and heredocs on Linux. The repo enforces `files.eol: "\n"` via [`devcontainer.json`](../../.devcontainer/devcontainer.json) settings; preserve LF when editing on Windows.

## Scope of `.devcontainer/README.md` — no duplication of the deployment guide

[`.devcontainer/README.md`](../../.devcontainer/README.md) is **the dev container reference** (what's installed, how it's configured, how to customize and troubleshoot it). It must **not** duplicate end-user deployment content that already lives in [`docs/DeploymentGuide.md`](../../docs/DeploymentGuide.md).

| Belongs in `.devcontainer/README.md` | Belongs in `docs/DeploymentGuide.md` |
|---|---|
| Files in this directory and what they do | Step-by-step `azd up` walkthrough |
| Dev Container Features and apt packages installed | `azd env set` configuration variables and defaults |
| VS Code extension list and settings | Two-phase deployment overview and the 6 `step_*` modules |
| Pre-installed Python dependencies | Deployment results (Fabric workspace tree, Foundry resources) |
| Port forwarding, mounts, host requirements | Cleanup (`azd down`) instructions |
| Dev-container-specific troubleshooting (`Permission denied` on `postCreateCommand`, `Failed Installing Extensions`, `pyodbc` driver missing) | General deployment errors |
| Customization (adding extensions / apt packages / Features) | Dev container itself appears only as Options 2 (Codespaces) and 3 (Dev Container) under §3 *Deployment Environment Setup* |

Hard rules:

- **Do not** include `az login` / `azd auth login` / `azd up` instructions in `.devcontainer/README.md`. Link to [`docs/DeploymentGuide.md`](../../docs/DeploymentGuide.md) instead.
- **Do not** restate the two-phase deployment, the 6 post-provision steps, or the optional configuration variables.
- **Do** keep a short *How to use this dev container* pointer at the top that sends Codespaces users to Option 2 and local Dev Containers users to Option 3 of the deployment guide.
- When the deployment guide changes (new option, renamed section, different `azd env set` variables), update the dev container README's pointer **only**, never the deployment content itself.

## Source of truth — keep in sync

When any of the columns below change, update the matching section of [`.devcontainer/README.md`](../../.devcontainer/README.md):

| Authoritative source | README section |
|---|---|
| `features` block in [`devcontainer.json`](../../.devcontainer/devcontainer.json) | *Features Included → Core Tools* |
| `installAptPackages` in the `common-utils` feature | *Features Included → Core Tools* (apt packages line) |
| Microsoft SQL Server ODBC install block in [`setup_env.sh`](../../.devcontainer/setup_env.sh) | *Features Included → SQL Server connectivity* and *Customization → Installing apt packages* |
| Dev tooling `pip install` block in [`post-create.sh`](../../.devcontainer/post-create.sh) | *Features Included → Python Development* |
| `requirements.txt` install block in [`post-create.sh`](../../.devcontainer/post-create.sh) | *Pre-installed Python Dependencies* |
| `customizations.vscode.extensions` in [`devcontainer.json`](../../.devcontainer/devcontainer.json) | *VS Code Extensions* |
| `forwardPorts` and `portsAttributes` in [`devcontainer.json`](../../.devcontainer/devcontainer.json) | *Container Configuration → Port forwarding* |
| `mounts` in [`devcontainer.json`](../../.devcontainer/devcontainer.json) | *Container Configuration → Mounted volumes* |
| `hostRequirements` in [`devcontainer.json`](../../.devcontainer/devcontainer.json) | *Container Configuration → Base configuration* |
| `postCreateCommand` in [`devcontainer.json`](../../.devcontainer/devcontainer.json) | *Container Configuration → Post-create commands* |
| Base image in [`Dockerfile`](../../.devcontainer/Dockerfile) | *Container Configuration → Base configuration* |
| Repo paths referenced from `post-create.sh` / `setup_env.sh` | *Files in this directory* (only update file descriptions; do not add a repo-wide tree) |
| Aliases set in [`post-create.sh`](../../.devcontainer/post-create.sh) | (Optional — only the user-visible workflow notes need to match) |
| Known errors (extension ID typos, missing `+x`, missing ODBC driver) | *Troubleshooting* |

## Cross-cutting documentation impact

Most `.devcontainer/` changes are local. Cross-check these files only when the change affects the **deployment surface**, not just the developer environment:

- [`docs/DeploymentGuide.md`](../../docs/DeploymentGuide.md) §3 *Deployment Commands* — only when prerequisites for `azd up` change in a way that affects users running outside the dev container (e.g. a new required tool that everyone now needs locally).
- [`docs/fabric/DeploymentGuideFabric.md`](../../docs/fabric/DeploymentGuideFabric.md) §1 *Prerequisites* — same condition as above.
- [`requirements.txt`](../../requirements.txt) — when adding a Python package that the local deployment scripts need. Do **not** add packages here purely for dev tooling; install those in [`post-create.sh`](../../.devcontainer/post-create.sh) instead.

Routine dev container changes (a new VS Code extension, an extra apt package, an additional alias) do not require updates to the deployment guides.

## Testing changes

After modifying any file in `.devcontainer/`:

1. **Rebuild the container** locally: Command Palette → *Dev Containers: Rebuild Container*. The build should succeed and `postCreateCommand` should run to completion with no errors.
2. **Verify in Codespaces** for changes that touch `setup_env.sh`, `postCreateCommand`, or the executable-bit assumptions. Codespaces clones the repo fresh each time and is the most likely place to surface permission / line-ending bugs.
3. Run a smoke check: `az --version`, `azd version`, `bicep --version`, `pwsh --version`, `python --version`, `python -c "import pyodbc; print(pyodbc.drivers())"`.
4. If you changed [`devcontainer.json`](../../.devcontainer/devcontainer.json) extensions, confirm none failed in the *Dev Containers* output channel (`Failed Installing Extensions: …`).
