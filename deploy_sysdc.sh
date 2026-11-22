#!/usr/bin/env bash
set -e

echo "=== GAMEVERSE SysDC Deployment Script ==="

# 1. Update system and install Python 3.12 / venv if needed
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y python3-pip python3-venv libpq-dev
elif command -v yum &> /dev/null; then
    sudo yum install -y python3-pip python3-devel
fi

# 2. Setup Virtual Environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 3. Install Requirements
echo "Installing dependencies..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# 4. Run Migrations
echo "Applying database migrations..."
./venv/bin/alembic upgrade head

# 5. Check Systemd Service setup
if [ -f "/etc/systemd/system/gameverse.service" ]; then
    echo "Reloading and restarting systemd service..."
    sudo systemctl daemon-reload
    sudo systemctl restart gameverse
    sudo systemctl status gameverse --no-pager
else
    echo "To setup auto-restart on SysDC VPS:"
    echo "sudo cp gameverse.service /etc/systemd/system/"
    echo "sudo systemctl daemon-reload"
    echo "sudo systemctl enable --now gameverse"
fi

echo "=== Deployment Finished Successfully! ==="
