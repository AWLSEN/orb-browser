"""
Simple agent example — one class, obvious methods.

Usage:
    ORB_API_KEY=orb_... python examples/agent_simple.py
"""

import asyncio
import os
from orb_browser import Browser

ORB_KEY = os.environ.get("ORB_API_KEY")
if not ORB_KEY:
    print("Set ORB_API_KEY")
    exit(1)


async def main():
    # Deploy a browser
    browser = await Browser.create(api_key=ORB_KEY)
    print(f"Computer ID: {browser.computer_id}")

    # Navigate
    await browser.go_to("https://news.ycombinator.com")
    print(f"Title: {await browser.title()}")
    print(f"URL: {await browser.url()}")

    # Screenshot
    img = await browser.screenshot("hn.png")
    print(f"Screenshot: {len(img)} bytes")

    # Scroll
    await browser.scroll("down", 500)
    await browser.wait(1)
    print(f"Scrolled. Title: {await browser.title()}")

    # Sleep
    computer_id = await browser.sleep()
    print(f"Sleeping. ID: {computer_id}")

    await asyncio.sleep(5)

    # Wake
    await browser.wake()
    print(f"Awake! Title: {await browser.title()}")

    # Navigate after wake
    await browser.go_to("https://example.com")
    print(f"After wake navigate: {await browser.title()}")

    # Clean up
    await browser.close()
    print("Done.")


asyncio.run(main())
