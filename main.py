"""
Pipeline Pilot — Browser-Use edition
-----------------------------------
Uses Browser-Use for robust Playwright actions and built-in tool schema.
"""

import os, json, dotenv, asyncio
from openai import OpenAI
from langchain_openai import ChatOpenAI
from playwright.async_api import async_playwright
from browser_use import Agent

bu_agent = None  # will be assigned inside main()

dotenv.load_dotenv()
client = OpenAI()
llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)

# ── custom HubSpot helpers ───────────────────────────────────────────
def go_to_deals_home():
    """
    Jump straight to the Deals board.
    Requires HUBSPOT_PORTAL_ID environment variable.
    """
    global bu_agent
    if bu_agent is None:
        return "error: agent not ready"
    portal = os.getenv("HUBSPOT_PORTAL_ID", "")
    if not portal:
        return "error: HUBSPOT_PORTAL_ID not set"
    bu_agent.page.goto(f"https://app.hubspot.com/contacts/{portal}/deals")
    return "OK"

def open_deal_by_search(query: str):
    """
    Use HubSpot’s global search bar to find a deal.
    """
    global bu_agent
    if bu_agent is None:
        return "error: agent not ready"
    p = bu_agent.page
    p.click('input[placeholder="Search"]')
    p.fill('input[placeholder="Search"]', query)
    p.press('input[placeholder="Search"]', "Enter")
    return "OK"

# ── Assistant runner ─────────────────────────────────────────────────
async def main():
    global bu_agent

    # 1️⃣  launch Playwright and open a page
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()

    # 2️⃣  user logs in manually
    await page.goto("https://app.hubspot.com/login")
    input("🔑  Log into HubSpot, then press <Enter> … ")

    # 3️⃣  instantiate Browser-Use agent bound to that page
    bu_agent = Agent(
        task="You are Pipeline Pilot, Jim’s sales co‑pilot for HubSpot tasks.",
        llm=llm,
        page=page
    )

    # 4️⃣  REPL — wait for user commands; one run per command
    print("🟢 Ready. Type a command (or 'quit').")
    while True:
        cmd = input("🧑 > ").strip()
        if cmd.lower() in {"quit", "exit", "q"}:
            break
        if not cmd:
            continue
        bu_agent.task = cmd
        await bu_agent.run(max_steps=25)

if __name__ == "__main__":
    asyncio.run(main())
