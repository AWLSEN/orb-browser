#!/bin/bash
# Start Xvfb as a separate process (not a child of Python)
# CRIU checkpoints --tree {pid} so Xvfb won't be included
Xvfb :99 -screen 0 1280x800x24 -ac &
export DISPLAY=:99
sleep 1

# Start the agent
exec python3 agent.py
