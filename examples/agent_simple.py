"""
Deploy a browser on Orb Cloud, browse, sleep, wake.

Usage: ORB_API_KEY=orb_... python examples/agent_simple.py
"""

import os
from orb_browser import OrbBrowser

orb = OrbBrowser(api_key=os.environ["ORB_API_KEY"])

# Deploy (~1-2 min)
orb.deploy()

# Browse
print(orb.navigate("https://news.ycombinator.com"))
orb.screenshot("hn.jpg")
print(f"Screenshot saved. URL: {orb.url()}")

# Sleep — frozen to NVMe, $0
computer_id = orb.computer_id
orb.sleep()

import time; time.sleep(5)

# Wake — ~500ms, everything restored
orb.wake()
print(f"After wake: {orb.url()}")

# Clean up
orb.destroy()
