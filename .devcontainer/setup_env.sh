#!/bin/bash

set -euo pipefail

echo ">>> Running setup_env.sh ..."

# Install Microsoft ODBC driver repo + msodbcsql18 if not already present.
# Run only the privileged block under sudo so the rest of the script stays
# in the vscode user's context (avoids a broken self re-exec that previously
# required this script to have the executable bit set).
if ! dpkg -s msodbcsql18 >/dev/null 2>&1; then
    echo ">>> Adding Microsoft SQL Server ODBC repository and installing msodbcsql18..."
    sudo bash -eu <<'EOF'
        curl -sSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
        curl -sSL https://packages.microsoft.com/config/debian/11/prod.list \
            > /etc/apt/sources.list.d/mssql-release.list

        export DEBIAN_FRONTEND=noninteractive
        apt-get update
        ACCEPT_EULA=Y apt-get install -y \
            msodbcsql18 \
            unixodbc \
            unixodbc-dev

        apt-get clean
        rm -rf /var/lib/apt/lists/*
EOF
else
    echo ">>> msodbcsql18 already installed, skipping."
fi

# Best-effort refresh of the working tree (non-fatal in Codespaces / detached states)
echo ">>> Refreshing repository state..."
git fetch --all --prune || echo "⚠️ git fetch skipped (non-fatal)"
git pull --ff-only || echo "⚠️ git pull skipped (non-fatal)"

# Provide execute permission to deployment helper scripts (only those that exist)
echo ">>> Ensuring helper scripts are executable..."
for script in \
    ./infra/scripts/checkquota_agentic_application.sh \
    ./infra/scripts/quota_check_params.sh \
    ./infra/scripts/docker-build.sh \
    ./infra/scripts/docker-build.ps1; do
    if [ -f "$script" ]; then
        chmod +x "$script"
        echo "   chmod +x $script"
    fi
done

echo ">>> setup_env.sh finished."