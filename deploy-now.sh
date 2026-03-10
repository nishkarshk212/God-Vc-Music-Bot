#!/usr/bin/env bash
set -euo pipefail

DEFAULT_IP_1="45.143.228.160"
DEFAULT_IP_2="140.245.240.202"
DEFAULT_USER="root"
DEFAULT_DIR="~/GodVCMusicBot"
DEFAULT_SERVICE="godvcbot"

echo "GodVCMusicBot — Deploy Latest Update"
echo "==================================="
echo

read -r -p "Server IP/host (Enter for ${DEFAULT_IP_1}): " SERVER_HOST
SERVER_HOST="${SERVER_HOST:-$DEFAULT_IP_1}"

if [[ "${SERVER_HOST}" == "${DEFAULT_IP_1}" ]]; then
  echo "Tip: if this isn't your VPS, try ${DEFAULT_IP_2}."
fi

read -r -p "SSH user (Enter for ${DEFAULT_USER}): " SERVER_USER
SERVER_USER="${SERVER_USER:-$DEFAULT_USER}"

read -r -p "Bot directory on server (Enter for ${DEFAULT_DIR}): " BOT_DIR
BOT_DIR="${BOT_DIR:-$DEFAULT_DIR}"

read -r -p "systemd service name (Enter for ${DEFAULT_SERVICE}): " SERVICE_NAME
SERVICE_NAME="${SERVICE_NAME:-$DEFAULT_SERVICE}"

echo
echo "Testing SSH connection to ${SERVER_USER}@${SERVER_HOST} ..."

SSH_COMMON_OPTS="-o ConnectTimeout=15 -o StrictHostKeyChecking=accept-new"

if ! ssh ${SSH_COMMON_OPTS} "${SERVER_USER}@${SERVER_HOST}" "echo SSH_OK >/dev/null"; then
  echo
  echo "SSH connection failed."
  echo
  echo "Manual update (run on the VPS):"
  echo "  cd ${BOT_DIR}"
  echo "  git pull origin main"
  echo "  source venv/bin/activate"
  echo "  pip install -r requirements.txt --upgrade"
  echo "  systemctl restart ${SERVICE_NAME}"
  exit 1
fi

echo "SSH OK. Deploying latest update..."
echo

ssh ${SSH_COMMON_OPTS} "${SERVER_USER}@${SERVER_HOST}" bash -s -- \
  "${BOT_DIR}" "${SERVICE_NAME}" <<'REMOTE'
set -euo pipefail

BOT_DIR="$1"
SERVICE_NAME="$2"

cd "${BOT_DIR}" || { echo "Bot directory not found: ${BOT_DIR}"; exit 1; }

echo "==> Pulling latest changes"
git pull origin main

if [[ -f "venv/bin/activate" ]]; then
  echo "==> Activating venv"
  # shellcheck disable=SC1091
  source venv/bin/activate
else
  echo "venv not found at ${BOT_DIR}/venv. Creating it..."
  python3 -m venv venv
  # shellcheck disable=SC1091
  source venv/bin/activate
fi

echo "==> Installing/upgrading dependencies"
python -m pip install --upgrade pip >/dev/null
pip install -r requirements.txt --upgrade --quiet

echo "==> Restarting service: ${SERVICE_NAME}"
systemctl restart "${SERVICE_NAME}"
sleep 3

echo
echo "==> Service status"
systemctl status "${SERVICE_NAME}" --no-pager | sed -n '1,12p'

echo
echo "==> Recent logs (last 30 lines)"
journalctl -u "${SERVICE_NAME}" -n 30 --no-pager
REMOTE

echo
echo "Done. If you want live logs:"
echo "  ssh ${SERVER_USER}@${SERVER_HOST} \"journalctl -u ${SERVICE_NAME} -f\""
