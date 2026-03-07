#!/bin/bash

# SSH Connection Script for GodVCMusicBot Deployment
# Run this from your Mac to connect to the server

SERVER_IP="140.245.240.202"
USERNAME="root"
PASSWORD="Akshay343402355468"

echo "🔌 Connecting to server..."
echo "Server: $SERVER_IP"
echo "User: $USERNAME"
echo ""

# Simple SSH connection
ssh -o StrictHostKeyChecking=no ${USERNAME}@${SERVER_IP}
