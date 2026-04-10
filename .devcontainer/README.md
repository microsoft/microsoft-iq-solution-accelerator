# Dev Container Configuration

This directory contains the development container configuration for the **Unified Data Foundation with Fabric** solution accelerator.

## What is a Dev Container?

A development container (or dev container for short) allows you to use a container as a full-featured development environment. This dev container is configured with all the tools and dependencies needed to work with this project.

## Features Included

### Core Tools
- **Python 3.11** with pip
- **Azure CLI** with Bicep extension
- **Azure Developer CLI (azd)**
- **PowerShell** (for cross-platform script execution)
- **Git** and **GitHub CLI**

### Python Development
- **Jupyter Lab** for notebook development
- **Black** code formatter
- **Flake8** linter
- **Pylance** language server
- **pytest** testing framework
- **mypy** type checker

### VS Code Extensions
- Python development extensions
- Azure tooling extensions
- Jupyter notebook support
- GitHub Copilot (if available)
- PowerShell extension
- YAML and JSON support

## Getting Started

### Prerequisites
- [Visual Studio Code](https://code.visualstudio.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Using the Dev Container

1. **Open in Dev Container**:
   - Open this repository in VS Code
   - Press `F1` or `Ctrl+Shift+P` to open the command palette
   - Type "Dev Containers: Reopen in Container" and select it
   - VS Code will build and start the dev container

2. **Alternative Methods**:
   - **GitHub Codespaces**: Click the "Code" button in GitHub → Codespaces → Create codespace
   - **Command Line**: Use `code .` in the repository root with the Dev Containers extension installed

### First Time Setup

After the container starts, authenticate with Azure:

```bash
# Authenticate with Azure CLI
az login

# Authenticate with Azure Developer CLI
azd auth login

# Set your admin email for Fabric deployment
azd env set AZURE_FABRIC_ADMIN_USER_EMAIL "your-email@domain.com"

# Deploy the solution
azd up
```

## Container Configuration

The dev container includes:

- **Base Image**: Microsoft's Python 3.11 dev container
- **Mounted Volumes**: Your local `.azure` directory for persistent authentication
- **Port Forwarding**: Ports 8000, 8080, and 8888 for web applications
- **Environment Variables**: Azure telemetry disabled by default

## Development Workflow

1. **Code Development**: Use VS Code with full IntelliSense and debugging support
2. **Testing**: Run `pytest` for unit tests
3. **Formatting**: Code is auto-formatted with Black on save
4. **Deployment**: Use `azd up` to deploy to Azure
5. **Notebooks**: Use `jupyter lab` for interactive development

## Troubleshooting

### Container Won't Start
- Ensure Docker Desktop is running
- Check that you have the Dev Containers extension installed
- Try rebuilding the container: Command Palette → "Dev Containers: Rebuild Container"

### Authentication Issues
- Your Azure credentials are mounted from `~/.azure` on your host machine
- If you get authentication errors, try `az login` again inside the container

### Permission Issues on Windows
- Ensure Docker Desktop has access to your drives
- Check Windows Subsystem for Linux (WSL) integration if using WSL

## Customization

You can customize the dev container by:

1. **Adding Extensions**: Edit `devcontainer.json` → `customizations.vscode.extensions`
2. **Installing Packages**: Modify `post-create.sh` script
3. **Environment Variables**: Add to `containerEnv` in `devcontainer.json`
4. **Port Forwarding**: Update `forwardPorts` array

## Benefits

✅ **Consistent Environment**: Same development environment for all team members  
✅ **Quick Setup**: Zero manual installation of tools and dependencies  
✅ **Isolated**: Container doesn't affect your host machine  
✅ **Pre-configured**: Ready to use with all necessary tools  
✅ **Cloud-ready**: Works with GitHub Codespaces  

---

For more information about dev containers, visit the [official documentation](https://containers.dev/).