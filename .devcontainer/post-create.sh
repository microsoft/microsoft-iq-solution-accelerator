#!/bin/bash

# Post-create script for dev container setup
# This script runs after the dev container is created to install additional dependencies

set -e

echo "🚀 Setting up Unified Data Foundation with Fabric development environment..."

# Note: Core tools already provided by devcontainer.json:
# - Python 3.x (base image) with pip and venv
# - Azure CLI + Bicep (azure-cli feature)
# - Git (git feature)  
# - GitHub CLI (github-cli feature)
# - PowerShell (powershell feature)
# - Azure Developer CLI (azd feature)
# - Common system tools: curl, wget, unzip, jq, tree, vim (base image)

# Update package lists
echo "📦 Updating package lists..."
sudo apt-get update

# Note: python3-venv, python3-pip, and python3-dev are not available as separate packages
# in the Python dev container base image. The venv module is built into Python 3.3+
# and pip is already pre-installed.

# Verify Python and pip are available
echo "🐍 Verifying Python installation..."
python3 --version
python3 -m pip --version

# Upgrade pip
echo "🐍 Upgrading pip..."
python3 -m pip install --upgrade pip

# Install Python requirements for the project
echo "📋 Installing Python dependencies globally..."

# Install Fabric requirements globally so they're pre-installed for deployment scripts
# This improves deployment script performance by avoiding repeated installations
if [ -f "./infra/scripts/fabric/requirements.txt" ]; then
    echo "📦 Installing Fabric script requirements globally..."
    python3 -m pip install -r "./infra/scripts/fabric/requirements.txt"
    echo "✅ Fabric script requirements installed successfully"
else
    echo "⚠️ Warning: ./infra/scripts/fabric/requirements.txt not found"
fi

# Verify that other requirements files exist (for reference)
if [ -f "./src/requirements.txt" ]; then
    echo "✅ Source requirements.txt found"
else
    echo "⚠️ Warning: ./src/requirements.txt not found"
fi

if [ -f "./infra/scripts/databricks/requirements.txt" ]; then
    echo "✅ Databricks script requirements.txt found"
else
    echo "ℹ️ Info: ./infra/scripts/databricks/requirements.txt not found (optional)"
fi

# Install additional development tools
echo "🛠️ Installing development tools..."
if ! python3 -m pip install --user \
    black \
    flake8 \
    pytest \
    mypy \
    bandit \
    jupyter \
    jupyterlab \
    ipykernel; then
    echo "❌ Failed to install development tools"
    exit 1
fi
echo "✅ Development tools installed successfully"

# Verify Azure CLI and azd installation (installed via devcontainer features)
echo "✅ Verifying tool installations..."
echo "Azure CLI version: $(az --version | head -n 1)"
echo "Azure Developer CLI version: $(azd version)"
echo "Python version: $(python --version)"
echo "Git version: $(git --version)"

# Set up additional git configuration (base git config handled by devcontainer feature)
echo "📝 Setting up additional git configuration..."
git config --global init.defaultBranch main
git config --global pull.rebase true
git config --global core.autocrlf input

# Create helpful aliases
echo "🔗 Setting up helpful aliases..."
echo 'alias ll="ls -la"' >> ~/.bashrc
echo 'alias tree="tree -I __pycache__"' >> ~/.bashrc
echo 'alias azd-env="azd env get-values"' >> ~/.bashrc
echo 'alias azd-up="azd up"' >> ~/.bashrc
echo 'alias azd-down="azd down"' >> ~/.bashrc

# Make scripts executable and fix line endings
echo "🔐 Making scripts executable and fixing line endings..."
find ./infra/scripts -name "*.sh" -type f -exec chmod +x {} \;
find ./infra/scripts -name "*.sh" -type f -exec sed -i 's/\r$//' {} \;

# Add virtual environment directories to .gitignore if not already present
echo "📝 Updating .gitignore for virtual environments..."
if ! grep -q "\.venv/" .gitignore 2>/dev/null; then
    echo "" >> .gitignore
    echo "# Python virtual environments" >> .gitignore
    echo ".venv/" >> .gitignore
    echo "*/.venv/" >> .gitignore
fi

# Create workspace info
echo "📄 Creating workspace information..."
cat > ~/WORKSPACE_INFO.md << 'EOF'

## Available Tools
- Azure CLI (`az`) + Bicep
- Azure Developer CLI (`azd`)
- Python 3.11+ with pip, venv, and common dependencies pre-installed
- PowerShell
- Git & GitHub CLI
- Jupyter Lab
- Development tools (black, flake8, pytest, mypy)
- System utilities (curl, wget, jq, tree, vim)

## Project Structure
- `/infra` - Infrastructure as Code (Bicep templates)
- `/src` - Source code and notebooks
- `/docs` - Documentation
- `/reports` - Power BI reports

## Helpful Commands
- `azd-env` - Show current azd environment variables
- `azd-up` - Deploy the solution
- `azd-down` - Clean up resources
- `tree` - Show directory structure (excluding __pycache__)
- `ll` - Detailed file listing
- `jupyter lab` - Start Jupyter Lab server

## Port Forwarding
- 8000, 8080, 8888 are forwarded for web applications

## Virtual Environment Notes
- Python venv module is available and configured in the container base
- Development tools are pre-installed globally for convenience
- Fabric deployment dependencies (Azure libraries, requests, etc.) are pre-installed globally for improved performance
- Additional project dependencies can be installed by deployment scripts in isolated virtual environments
- This approach balances convenience with flexibility while avoiding version conflicts

Enjoy coding! 🎉
EOF

echo "✨ Dev container setup complete!"
echo "📖 Check ~/WORKSPACE_INFO.md for quick start instructions"
echo ""
echo "🎯 Next steps:"
echo "   1. Configure your Git user name and email using 'git config --global user.name \"Your Name\"' and 'git config --global user.email \"your-email@domain.com\"'"
echo "   2. Run 'az login' to authenticate with Azure"
echo "   3. Run 'azd auth login' to authenticate with Azure Developer CLI"
echo "   4. Deploy the solution: azd up"
echo ""
echo "🔧 Development shortcuts:"
echo "   - Use 'azd up' to deploy the full solution"
echo "   - Use PowerShell scripts in infra/scripts/ for component-specific deployments"