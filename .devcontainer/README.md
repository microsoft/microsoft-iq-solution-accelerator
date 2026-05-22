# Dev Container Configuration

This directory contains the development container configuration for the **Microsoft IQ Solution Accelerator**. It defines a reproducible Linux environment with every tool needed to author Bicep templates, run the Python deployment scripts under [`infra/scripts/`](../infra/scripts/), execute Fabric notebooks, and run `azd up`.

## Files in this directory

| File | Purpose |
|---|---|
| [`devcontainer.json`](./devcontainer.json) | Dev container manifest: base image build, [dev container Features](https://containers.dev/features), VS Code extensions and settings, mounts, port forwarding, and the `postCreateCommand`. |
| [`Dockerfile`](./Dockerfile) | Base image (`mcr.microsoft.com/devcontainers/python:3.11-bullseye`) with a fix that removes the expired Yarn apt repo to avoid GPG errors. |
| [`post-create.sh`](./post-create.sh) | Runs as the `vscode` user after the container is built. Installs Python project dependencies, dev tooling, helpful aliases, and fixes script permissions / line endings. |
| [`setup_env.sh`](./setup_env.sh) | Runs after `post-create.sh`. Installs the Microsoft SQL Server ODBC driver (`msodbcsql18`) under `sudo`, then refreshes the working tree and ensures helper scripts under [`infra/scripts/`](../infra/scripts/) are executable. |
| [`.dockerignore`](./.dockerignore) | Excludes files from the Docker build context. |

## What is a Dev Container?

A development container (or dev container for short) lets you use a container as a full-featured development environment. This one is configured with all the tools and dependencies needed to work with the accelerator and is also the environment used by [GitHub Codespaces](https://github.com/features/codespaces).

## Features Included

### Core Tools (provided by [Dev Container Features](https://containers.dev/features))
- **Python 3.11** (base image) with `pip` and `venv`
- **Azure CLI** with **Bicep** (`ghcr.io/devcontainers/features/azure-cli`)
- **Azure Developer CLI (azd)** (`ghcr.io/azure/azure-dev/azd`)
- **PowerShell** (`ghcr.io/devcontainers/features/powershell`) — required for cross-platform `azd` hooks via [`Run-PythonScript.ps1`](../infra/scripts/utils/Run-PythonScript.ps1)
- **Git** (`ghcr.io/devcontainers/features/git`) and **GitHub CLI** (`ghcr.io/devcontainers/features/github-cli`)
- **Docker-in-Docker** (`ghcr.io/devcontainers/features/docker-in-docker`) — lets you build and run containers from inside the dev container
- **Common utilities** (`ghcr.io/devcontainers/features/common-utils`) — installs the apt packages `unixodbc`, `unixodbc-dev`, and `bash`

### SQL Server connectivity
- **Microsoft ODBC Driver 18** (`msodbcsql18`) — installed by [`setup_env.sh`](./setup_env.sh) using the Microsoft Debian package repository

### Python Development (installed via [`post-create.sh`](./post-create.sh))
- **Jupyter Lab** + `ipykernel` for notebook development
- **Black** formatter, **Flake8** linter, **mypy** type checker, **Bandit** security scanner
- **pytest** test framework
- **Pylance** language server (via the VS Code extension)

### VS Code Extensions (from [`devcontainer.json`](./devcontainer.json))
- GitHub: `GitHub.copilot`, `GitHub.copilot-chat`, `GitHub.vscode-github-actions`
- Azure: `ms-azuretools.azure-dev`, `ms-vscode.azurecli`, `ms-azuretools.vscode-bicep`
- Python: `ms-python.python`, `ms-python.vscode-pylance`, `ms-python.black-formatter`
- Jupyter: `ms-toolsai.jupyter`, `ms-toolsai.vscode-jupyter-cell-tags`, `ms-toolsai.vscode-jupyter-slideshow`
- Microsoft Fabric: `synapsevscode.synapse`
- Other: `ms-vscode.powershell`, `redhat.vscode-yaml`

### Pre-installed Python Dependencies
[`post-create.sh`](./post-create.sh) installs the following globally with `python3 -m pip install`:
- All packages in the repo-root [`requirements.txt`](../requirements.txt) — required by the local deployment scripts in [`infra/scripts/common/`](../infra/scripts/common/), [`infra/scripts/fabric/`](../infra/scripts/fabric/), and [`infra/scripts/foundry/`](../infra/scripts/foundry/)
- Optional [`src/fabric/datagen/requirements.txt`](../src/fabric/datagen/requirements.txt) — for the sample data generators
- `fabric-launcher[dev]` in editable mode — only when a sibling `../fabric-launcher` checkout exists (multi-root workspace)

> Note: The Fabric installer notebook ([`fabric_solution_installer.ipynb`](../infra/fabric/deploy/fabric_solution_installer.ipynb)) runs **inside the Fabric workspace**, not in this container. It manages its own dependencies via `%pip install`; the container's Python packages do not affect it.

## How to use this dev container

This README is a **reference for the dev container itself** — what's installed, how it's configured, and how to customize it. For end-to-end deployment instructions (prerequisites, `azd up`, optional configuration variables, expected results, cleanup), see the single source of truth: [`docs/DeploymentGuide.md`](../docs/DeploymentGuide.md).

Pick the matching option in *§3 Deployment Environment Setup*:

- **GitHub Codespaces** → [Option 2](../docs/DeploymentGuide.md#deployment-environment-setup) (this dev container runs in the cloud).
- **Local VS Code + Docker Desktop** → [Option 3](../docs/DeploymentGuide.md#deployment-environment-setup) (this dev container runs locally).

Both options use the configuration documented below; the deployment guide describes only what to run inside the container.

## Container Configuration

### Base configuration
- **Base image**: `mcr.microsoft.com/devcontainers/python:3.11-bullseye` (see [`Dockerfile`](./Dockerfile))
- **Remote user**: `vscode` (non-root)
- **Host requirement**: 4 GB memory minimum (see `hostRequirements` in [`devcontainer.json`](./devcontainer.json))

### Post-create commands
[`devcontainer.json`](./devcontainer.json) chains two scripts in `postCreateCommand`:
```
bash .devcontainer/post-create.sh && bash .devcontainer/setup_env.sh
```

### Mounted volumes
- **Azure credentials**: `${HOME}/.azure` (or `${USERPROFILE}/.azure` on Windows hosts) is bind-mounted to `/home/vscode/.azure` so `az` / `azd` sessions persist between container rebuilds.

### Port forwarding
- **8000, 8080** — generic web applications
- **8888** — Jupyter Lab (auto-notified when forwarded)
- **50505** — *Application* (auto-notified when forwarded)

### Environment
- Linux line endings (`\n`) enforced via `files.eol`
- Python formatting with Black on save; `source.organizeImports` runs on save
- Default Linux terminal profile: `bash`

## Development Workflow

1. **Code Development** — use VS Code with full IntelliSense and debugging support.
2. **Testing** — run `pytest` for unit tests.
3. **Formatting** — code is auto-formatted with Black on save; imports are organized via `source.organizeImports`.
4. **Deployment** — see [`docs/DeploymentGuide.md`](../docs/DeploymentGuide.md).
5. **Notebooks** —
   - Use `jupyter lab` for local interactive development.
   - Use the Microsoft Fabric extension to sync with a Fabric workspace.
   - The orchestration notebook [`fabric_solution_installer.ipynb`](../infra/fabric/deploy/fabric_solution_installer.ipynb) executes inside Fabric, not in this container.
6. **Data Generation** — run scripts in [`src/fabric/datagen/`](../src/fabric/datagen/) to create sample data.

## Troubleshooting

### Container won't start
- Ensure Docker Desktop is running.
- Check that you have the Dev Containers extension installed.
- Try rebuilding: Command Palette → *Dev Containers: Rebuild Container*.

### `postCreateCommand` exits with `Permission denied` (exit 126)
This happens if `.devcontainer/setup_env.sh` is invoked with `exec` rather than via `bash`. The current `postCreateCommand` runs both scripts with `bash .devcontainer/<script>.sh`, which does not require the executable bit. If you customize the command, keep using `bash <script>` so the scripts work even when Codespaces clones them without `+x`.

### `Failed Installing Extensions`
Verify every extension ID in [`devcontainer.json`](./devcontainer.json) resolves on the [VS Code Marketplace](https://marketplace.visualstudio.com/vscode). The Azure CLI Tools extension is `ms-vscode.azurecli` (not `ms-azuretools.vscode-azurecli`), and JSON support is built in to VS Code (no `ms-vscode.vscode-json` extension exists).

### Authentication issues
- Your Azure credentials are mounted from the host's `~/.azure` (or `%USERPROFILE%\.azure`). If `az login` works on the host, it should work in the container.
- Re-authenticate inside the container if needed:
  ```bash
  az login
  azd auth login
  ```

### Permission issues on Windows
- Ensure Docker Desktop has access to your drives (Settings → Resources → File Sharing).
- The WSL2 backend is recommended for performance.

### SQL Server / `pyodbc` errors
If `pyodbc.connect(...)` cannot find a driver, [`setup_env.sh`](./setup_env.sh) may have failed to install `msodbcsql18`. Re-run it manually:
```bash
bash .devcontainer/setup_env.sh
```

### Deployment errors
- Verify Azure permissions (see Prerequisites in the [main README](../README.md)).
- Check current `azd` env values: `azd env get-values`.
- Review deployment logs in `.azure/<environment>/` and the script output captured by [`infra/scripts/utils/Run-PythonScript.ps1`](../infra/scripts/utils/Run-PythonScript.ps1).

### Multi-root workspace
If you open this repo together with a sibling [fabric-launcher](https://github.com/microsoft/fabric-launcher) checkout:
- [`post-create.sh`](./post-create.sh) detects `../fabric-launcher` and installs it in editable mode (`pip install -e ../fabric-launcher[dev]`).
- Both repositories are accessible from the same container; reference paths via `../fabric-launcher/`.

## Additional Resources

- [Azure Developer CLI Documentation](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- [Microsoft Fabric Documentation](https://learn.microsoft.com/fabric/)
- [Dev Containers Documentation](https://code.visualstudio.com/docs/devcontainers/containers)
- [Dev Container Features (containers.dev)](https://containers.dev/features)
- [Top-level Deployment Guide](../docs/DeploymentGuide.md)
- [Fabric Deployment Guide (manual)](../docs/fabric/DeploymentGuideFabricManual.md)

## Customization

You can customize the dev container by:

1. **Adding/removing extensions** — edit [`devcontainer.json`](./devcontainer.json) → `customizations.vscode.extensions`. Verify each ID exists on the [VS Code Marketplace](https://marketplace.visualstudio.com/vscode) before committing.
2. **Installing Python packages** — add to the repo-root [`requirements.txt`](../requirements.txt) (used by the local deployment scripts) or modify [`post-create.sh`](./post-create.sh) for global dev tooling.
3. **Installing apt packages** — add to the `installAptPackages` list in the `common-utils` feature in [`devcontainer.json`](./devcontainer.json), or to the `apt-get install` block in [`setup_env.sh`](./setup_env.sh) for packages that need a custom repository.
4. **Adding a Dev Container Feature** — add to the `features` block in [`devcontainer.json`](./devcontainer.json). Browse available features at [containers.dev/features](https://containers.dev/features).
5. **Environment variables** — add a `containerEnv` block to [`devcontainer.json`](./devcontainer.json), or set them via `azd env set` for deployment-time variables.
6. **Port forwarding** — update `forwardPorts` and `portsAttributes` in [`devcontainer.json`](./devcontainer.json).

## Benefits

- **Consistent environment** — every team member and Codespaces user gets the same toolchain.
- **Quick setup** — zero manual installation of Azure CLI, azd, PowerShell, Bicep, Python, ODBC driver, etc.
- **Isolated** — the container does not affect your host machine.
- **Pre-configured** — ready to run `azd up` immediately after authentication.
- **Cloud-ready** — the same configuration is used by GitHub Codespaces.

---

For more information about dev containers, visit the [official documentation](https://containers.dev/).