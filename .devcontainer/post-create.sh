#!/bin/bash

# Post-create script for dev container setup
# This script runs after the dev container is created to install additional dependencies

set -e

echo "🚀 Setting up Microsoft IQ Solution Accelerator development environment..."

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

# Install main Fabric requirements globally (used by deployment scripts)
# This improves deployment script performance by avoiding repeated installations
if [ -f "./requirements.txt" ]; then
    echo "📦 Installing main Fabric requirements globally..."
    python3 -m pip install -r "./requirements.txt"
    echo "✅ Main Fabric requirements installed successfully"
else
    echo "⚠️ Warning: ./requirements.txt not found"
fi

# Install data generation requirements (optional)
if [ -f "./src/fabric/datagen/requirements.txt" ]; then
    echo "📦 Installing data generation requirements..."
    python3 -m pip install -r "./src/fabric/datagen/requirements.txt"
    echo "✅ Data generation requirements installed successfully"
else
    echo "ℹ️ Info: ./src/fabric/datagen/requirements.txt not found (optional)"
fi

# Install fabric-launcher if in multi-root workspace
if [ -d "../fabric-launcher" ]; then
    echo "📦 Installing fabric-launcher in editable mode..."
    python3 -m pip install -e "../fabric-launcher[dev]"
    echo "✅ fabric-launcher installed successfully"
else
    echo "ℹ️ Info: fabric-launcher not found in workspace (optional)"
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
find ./infra/scripts -type f -name "*.sh" -exec chmod +x {} \;
find ./infra/scripts -type f -name "*.py" -exec chmod +x {} \;
find ./infra/scripts -type f -name "*.sh" -exec sed -i 's/\r$//' {} \;

# Add virtual environment directories to .gitignore if not already present
echo "📝 Updating .gitignore for virtual environments..."
if ! grep -q "\.venv/" .gitignore 2>/dev/null; then
    echo "" >> .gitignore
    echo "# Python virtual environments" >> .gitignore
    echo ".venv/" >> .gitignore
    echo "*/.venv/" >> .gitignore
fi

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "📖 Quick Start:"
echo "  1. Authenticate: az login && azd auth login"
echo "  2. Configure: azd env set AZURE_FABRIC_ADMIN_USER_EMAIL your-email@domain.com"
echo "  3. Deploy: azd up"
echo ""
echo "💡 Helpful aliases:"
echo "  - azd-env   : Show current azd environment variables"
echo "  - azd-up    : Deploy the solution"
echo "  - azd-down  : Clean up resources"
echo "  - ll        : Detailed file listing"
echo "  - tree      : Directory structure (excluding __pycache__)"
echo ""