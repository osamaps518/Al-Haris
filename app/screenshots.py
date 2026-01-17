import requests
import os

SCREENSHOT_API_URL = "https://api.screenshotone.com/take"

def capture_screenshot(url: str) -> str | None:
    """Returns direct API URL that serves the screenshot."""
    try:
        access_key = os.getenv("SCREENSHOT_API_KEY")
        params = {
            "access_key": access_key,
            "url": url,
            "format": "png",
            "viewport_width": 1280,
            "viewport_height": 800,
        }
        # Verify it works first
        response = requests.get(SCREENSHOT_API_URL, params=params, timeout=30)
        response.raise_for_status()
        
        # Return the URL that serves the image (it's cached on their end)
        from urllib.parse import urlencode
        return f"{SCREENSHOT_API_URL}?{urlencode(params)}"
    except Exception as e:
        print(f"Screenshot capture failed: {e}")
        return None