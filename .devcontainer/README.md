# Dev Container Configuration

This directory contains the development container configuration for the **Microsoft IQ Solution Accelerator**.

## What is a Dev Container?

A development container (or dev container for short) allows you to use a container as a full-featured development environment. This dev container is configured with all the tools and dependencies needed to work with this project.

## Features Included

### Core Tools
- **Python 3.11** with pip and venv
- **Azure CLI** with Bicep extension
- **Azure Developer CLI (azd)** for deployment automation
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
- Python development extensions (Pylance, Black formatter)
- Azure tooling extensions (Azure CLI, Azure Developer CLI, Bicep)
- Jupyter notebook support
- Microsoft Fabric extension (synapsevscode.synapse)
- GitHub Copilot (if available)
- PowerShell extension
- YAML and JSON support

### Pre-installed Dependencies
- **Fabric deployment requirements** (azure-identity, requests, azure-mgmt-fabric)
- **Data generation tools** (pandas, numpy, matplotlib)
- **fabric-launcher** (if in multi-root workspace)

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

After the container starts, authenticate with Azure and deploy:

```bash
# Authenticate with Azure CLI
az login

# Authenticate with Azure Developer CLI
azd auth login

# Set your admin email for Fabric deployment
azd env set AZURE_FABRIC_ADMIN_USER_EMAIL "your-email@domain.com"

# Deploy the solution (provisions infrastructure and installs Fabric workspace)
azd up
```

The `azd up` command will:
1. Provision Azure resources using Bicep templates from `infra/`
2. Run the post-provision hook that executes `infra/scripts/fabric/install_fabric_solution.py`
3. Deploy the Fabric workspace items from `src/fabric/fabric_workspace/`

## Container Configuration

### Base Configuration
- **Base Image**: Microsoft's Python 3.11 dev container (Debian Bullseye)
- **Remote User**: vscode (non-root)
- **Working Directory**: Repository root

### Mounted Volumes
- **Azure credentials**: `~/.azure` mounted from host for persistent authentication

### Port Forwarding
- **8000, 8080**: Web applications
- **8888**: Jupyter Lab (auto-notified when forwarded)

### Environment
- Linux line endings (`\n`) enforced
- Python formatting with Black on save
- Azure telemetry disabled by default

## Development Workflow

1. **Code Development**: Use VS Code with full IntelliSense and debugging support
2. **Testing**: Run `pytest` for unit tests
3. **Formatting**: Code is auto-formatted with Black on save
4. **Deployment**: Use `azd up` to deploy infrastructure and Fabric workspace
5. **Notebooks**: 
   - Use `jupyter lab` for local interactive development
   - Use the Fabric extension for syncing with Fabric workspace
6. **Data Generation**: Run scripts in `src/fabric/datagen/` to create sample data

## Repository Structure

```
.
├── infra/                          # Infrastructure as Code
│   ├── main.bicep                  # Main Bicep template
│   ├── main.parameters.json        # Deployment parameters
│   └── scripts/fabric/             # Deployment scripts
│       ├── fabric_api.py           # Fabric API client
│       ├── graph_api.py            # Microsoft Graph API client
│       ├── install_fabric_solution.py  # Installs Fabric workspace
│       └── remove_fabric_solution.py   # Removes Fabric workspace
├── src/fabric/                     # Fabric solution artifacts
│   ├── fabric_workspace/           # Workspace items (Git format)
│   ├── datagen/                    # Sample data generators
│   ├── notebooks/                  # Development notebooks
│   └── dashboards/                 # Power BI dashboards
├── docs/                           # Documentation
│   └── fabric/                     # Fabric-specific docs
│       ├── DeploymentGuideFabric.md
│       └── DeploymentGuideFabricManual.md
└── requirements.txt                # Python dependencies for deployment
```

## Troubleshooting

### Container Won't Start
- Ensure Docker Desktop is running
- Check that you have the Dev Containers extension installed
- Try rebuilding the container: Command Palette → "Dev Containers: Rebuild Container"

### Authentication Issues
- Your Azure credentials are mounted from `~/.azure` on your host machine
- If you get authentication errors, try running inside the container:
  ```bash
  az login
  azd auth login
  ```

### Permission Issues on Windows
- Ensure Docker Desktop has access to your drives (Settings → Resources → File Sharing)
- WSL2 backend is recommended for better performance

### Deployment Errors
- Verify you have the required Azure permissions (see Prerequisites in main README)
- Check that required environment variables are set:
  ```bash
  azd env get-values
  ```
- Review deployment logs in `.azure/<environment>/` directory

### Multi-Root Workspace
If you're using this with the fabric-launcher repository in a multi-root workspace:
- The post-create script will automatically install fabric-launcher in editable mode
- Both repositories will be accessible from the same container
- Use relative paths `../fabric-launcher/` to reference the other workspace

## Additional Resources

- [Azure Developer CLI Documentation](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- [Microsoft Fabric Documentation](https://learn.microsoft.com/fabric/)
- [Dev Containers Documentation](https://code.visualstudio.com/docs/devcontainers/containers)
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