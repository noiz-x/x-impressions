import asyncio
import os
import random
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

with open("user-agents.txt") as file:
    user_agents = [line.strip() for line in file if line.strip()]

async def scrape_with_tor(playwright, url: str, iteration: int, headers: dict, proxy_config: dict):
    browser = await playwright.chromium.launch(headless=True, proxy=proxy_config) 
    page = await browser.new_page()
    
    await page.context.clear_cookies()
    await page.set_extra_http_headers(headers)
    
    page.set_default_navigation_timeout(60000)
    
    await page.goto(url, wait_until="networkidle")
    
    try:
        await page.wait_for_selector("article, div[data-testid='tweet']", timeout=60000)
    except Exception as e:
        print(f"Iteration {iteration}: Expected selectors not found: {e}")
        screenshot_path = f"screenshot_{iteration}.png"
        await page.screenshot(path=screenshot_path)
        print(f"Iteration {iteration}: Screenshot saved to {screenshot_path}")
    
    await asyncio.sleep(2)
    
    title = await page.title()
    print(f"Iteration {iteration}: Title: {title} (via Tor proxy, new browser instance)")
    
    await browser.close()

async def main():
    iterations = 10
    proxy_config = {"server": "socks5://127.0.0.1:9050"}
    target_url = os.getenv("link")
    
    async with async_playwright() as playwright:
        for i in range(iterations):
            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://x.com/"
            }
            print(f"Iteration {i+1} headers: {headers}")
            await scrape_with_tor(playwright, target_url, i + 1, headers, proxy_config)
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
