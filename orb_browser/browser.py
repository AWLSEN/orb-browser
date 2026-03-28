"""
Agent-friendly browser interface.

One class, obvious methods, handles all lifecycle automatically.

    browser = await Browser.create(api_key="orb_...")
    await browser.go_to("https://example.com")
    text = await browser.get_text()
    await browser.sleep()
    await browser.wake()
    await browser.close()
"""

from __future__ import annotations

import asyncio
from typing import Any

from orb_browser.client import OrbBrowser


class Browser:
    """
    A browser that runs on Orb Cloud.

    Handles deploy, CDP connection, browser control, sleep/wake, cleanup.
    Agents interact with this class — nothing else needed.
    """

    def __init__(self, orb: OrbBrowser, _inner: Any = None, _agent_port: int | None = None):
        self._orb = orb
        self._inner = _inner  # browser_use.Browser instance
        self._agent_port = _agent_port

    @classmethod
    async def create(cls, api_key: str, **deploy_kwargs) -> "Browser":
        """
        Deploy a new browser on Orb Cloud and connect to it.

        Takes 1-3 minutes (installs Chrome). Returns a ready-to-use browser.

        Usage:
            browser = await Browser.create(api_key="orb_...")
            await browser.go_to("https://example.com")
        """
        orb = OrbBrowser(api_key=api_key)
        cdp_url = orb.deploy(**deploy_kwargs)
        inner = await cls._connect(cdp_url)
        return cls(orb=orb, _inner=inner, _agent_port=orb.agent_port)

    @classmethod
    async def connect(cls, api_key: str, computer_id: str, agent_port: int | None = None) -> "Browser":
        """
        Wake and connect to an existing sleeping browser.

        Usage:
            browser = await Browser.connect(api_key="orb_...", computer_id="0a112172-...")
            # Still logged in, same cookies, same page
        """
        orb = OrbBrowser(api_key=api_key)

        if agent_port:
            orb.computer_id = computer_id
            orb.short_id = computer_id[:8]
            orb.agent_port = agent_port
            orb._state = "sleeping"
            cdp_url = orb.wake()
        else:
            cdp_url = orb.connect(computer_id=computer_id, agent_port=0)
            # Try to get agent port from agents list
            agents = orb._orb("GET", f"/v1/computers/{computer_id}/agents")
            if agents.get("agents"):
                orb.agent_port = agents["agents"][0]["port"]

        inner = await cls._connect(cdp_url)
        return cls(orb=orb, _inner=inner, _agent_port=orb.agent_port)

    # -- Navigation --

    async def go_to(self, url: str) -> None:
        """Navigate to a URL."""
        await self._inner.navigate_to(url)

    async def back(self) -> None:
        """Go back."""
        cdp = self._inner.cdp_client
        await cdp.send("Page.navigatedWithinDocument", {"url": "javascript:history.back()"})

    # -- Content --

    async def get_text(self) -> str:
        """Get the page content as readable text."""
        return await self._inner.get_state_as_text()

    async def get_html(self) -> str:
        """Get the page HTML."""
        cdp = self._inner.cdp_client
        result = await cdp.send("Runtime.evaluate", {
            "expression": "document.documentElement.outerHTML",
            "returnByValue": True,
        })
        return result.get("result", {}).get("value", "")

    async def title(self) -> str:
        """Get the page title."""
        return await self._inner.get_current_page_title()

    async def url(self) -> str:
        """Get the current URL."""
        return await self._inner.get_current_page_url()

    async def screenshot(self, path: str | None = None) -> bytes:
        """Take a screenshot. Returns PNG bytes."""
        return await self._inner.take_screenshot(path=path)

    # -- Interaction via CDP --

    async def click(self, selector: str) -> None:
        """Click an element by CSS selector."""
        cdp = self._inner.cdp_client
        # Find the element
        doc = await cdp.send("DOM.getDocument")
        node = await cdp.send("DOM.querySelector", {
            "nodeId": doc["root"]["nodeId"],
            "selector": selector,
        })
        if not node.get("nodeId"):
            raise ValueError(f"Element not found: {selector}")
        # Get its position
        box = await cdp.send("DOM.getBoxModel", {"nodeId": node["nodeId"]})
        quad = box["model"]["content"]
        x = (quad[0] + quad[2] + quad[4] + quad[6]) / 4
        y = (quad[1] + quad[3] + quad[5] + quad[7]) / 4
        # Click
        for event_type in ["mousePressed", "mouseReleased"]:
            await cdp.send("Input.dispatchMouseEvent", {
                "type": event_type, "x": x, "y": y, "button": "left", "clickCount": 1,
            })

    async def fill(self, selector: str, value: str) -> None:
        """Fill an input field by CSS selector."""
        await self.click(selector)
        # Focus and clear
        cdp = self._inner.cdp_client
        await cdp.send("Runtime.evaluate", {
            "expression": f"document.querySelector('{selector}').value = ''"
        })
        # Type the value
        for char in value:
            for event_type in ["keyDown", "keyUp"]:
                await cdp.send("Input.dispatchKeyEvent", {
                    "type": event_type, "text": char,
                })

    async def type(self, text: str) -> None:
        """Type text into the currently focused element."""
        cdp = self._inner.cdp_client
        for char in text:
            await cdp.send("Input.dispatchKeyEvent", {"type": "keyDown", "text": char})
            await cdp.send("Input.dispatchKeyEvent", {"type": "keyUp", "text": char})

    async def press(self, key: str) -> None:
        """Press a key (e.g., 'Enter', 'Tab', 'Escape')."""
        cdp = self._inner.cdp_client
        await cdp.send("Input.dispatchKeyEvent", {"type": "keyDown", "key": key})
        await cdp.send("Input.dispatchKeyEvent", {"type": "keyUp", "key": key})

    async def scroll(self, direction: str = "down", amount: int = 500) -> None:
        """Scroll the page. direction: 'up' or 'down'."""
        cdp = self._inner.cdp_client
        delta = amount if direction == "down" else -amount
        await cdp.send("Input.dispatchMouseEvent", {
            "type": "mouseWheel", "x": 400, "y": 400,
            "deltaX": 0, "deltaY": delta,
        })

    async def evaluate(self, expression: str) -> Any:
        """Execute JavaScript and return the result."""
        cdp = self._inner.cdp_client
        result = await cdp.send("Runtime.evaluate", {
            "expression": expression, "returnByValue": True,
        })
        return result.get("result", {}).get("value")

    async def wait(self, seconds: float) -> None:
        """Wait for a number of seconds."""
        await asyncio.sleep(seconds)

    # -- Cookies & State --

    async def cookies(self) -> list:
        """Get all cookies."""
        return await self._inner.cookies()

    async def set_cookies(self, cookies: list[dict]) -> None:
        """Set cookies."""
        cdp = self._inner.cdp_client
        await cdp.send("Network.setCookies", {"cookies": cookies})

    # -- Tabs --

    async def new_tab(self, url: str | None = None) -> None:
        """Open a new tab."""
        await self._inner.new_page(url)

    async def tabs(self) -> list:
        """List open tabs."""
        return await self._inner.get_tabs()

    # -- Sleep / Wake --

    async def sleep(self) -> str:
        """
        Checkpoint the browser to NVMe. Costs $0 while sleeping.
        Returns the computer_id — save it to wake this browser later.

        WebSocket connection drops. Call wake() or Browser.connect() to resume.
        """
        await self._disconnect()
        self._orb.sleep()
        return self._orb.computer_id

    async def wake(self) -> None:
        """
        Restore the browser from checkpoint. ~500ms.
        Automatically reconnects — ready to use immediately after.
        """
        cdp_url = self._orb.wake()
        self._inner = await self._connect(cdp_url)

    # -- Lifecycle --

    @property
    def computer_id(self) -> str | None:
        """The Orb computer ID. Save this to reconnect later."""
        return self._orb.computer_id

    @property
    def state(self) -> str:
        """Current state: init, deploying, running, sleeping, destroyed."""
        return self._orb.state

    @property
    def inner(self):
        """Access the underlying browser_use.Browser for advanced usage."""
        return self._inner

    async def close(self) -> None:
        """Disconnect and destroy the VM."""
        await self._disconnect()
        self._orb.destroy()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    # -- Internal --

    @staticmethod
    async def _connect(cdp_url: str):
        from browser_use import Browser as BUBrowser
        inner = BUBrowser(cdp_url=cdp_url)
        await inner.start()
        return inner

    async def _disconnect(self):
        if self._inner:
            try:
                await self._inner.stop()
            except Exception:
                pass
            self._inner = None
