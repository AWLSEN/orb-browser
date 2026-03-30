"""
Log into a site manually, then checkpoint the session.

1. Deploys a browser
2. Opens the live view in your browser
3. You log in manually (click, type, do 2FA)
4. Script checkpoints the logged-in session
5. Next time, wake and you're still logged in

Usage: ORB_API_KEY=orb_... python examples/manual_login.py
"""

import os
import webbrowser
from orb_browser import OrbBrowser

orb = OrbBrowser(api_key=os.environ["ORB_API_KEY"])

# Deploy
orb.deploy()

# Navigate to login page
orb.navigate("https://x.com/login")

# Open live view in your browser
print(f"\n{'='*50}")
print(f"Open this URL in your browser to log in:")
print(f"\n  {orb.live_url}\n")
print(f"{'='*50}")
print(f"\nClick, type, do 2FA — whatever you need.")
print(f"When you're logged in, come back here and press Enter.\n")

webbrowser.open(orb.live_url)
input("Press Enter when logged in... ")

# Verify
info = orb.url()
cookies = orb.cookies()
print(f"\nURL: {info['url']}")
print(f"Cookies: {len(cookies)}")
orb.screenshot("logged_in.jpg")
print(f"Screenshot saved to logged_in.jpg")

# Save the computer ID for later
computer_id = orb.computer_id
agent_port = orb.agent_port

# Checkpoint — session frozen, $0
orb.sleep()
print(f"\nSession checkpointed! Computer ID: {computer_id}")
print(f"Agent port: {agent_port}")
print(f"\nTo wake later:")
print(f"  orb = OrbBrowser(api_key='...')")
print(f"  orb.connect('{computer_id}', {agent_port})")
print(f"  orb.wake()")
print(f"  # Still logged in!")
