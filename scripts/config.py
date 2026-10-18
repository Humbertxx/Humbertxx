from pathlib import Path
import os

FEED = f"https://www.goodreads.com/review/list_rss/{os.getenv('USER_ID', '').strip()}?shelf={os.getenv('SHELF', '').strip()}"

README = Path(__file__).resolve().parent.parent / "README.md"
START = "<!-- BOOKS:START -->"
END = "<!-- BOOKS:END -->"

# Goodreads serves a 403 to the default urllib agent.
HEADERS = {"User-Agent": "Humbertxx-profile-readme/1.0 (+https://github.com/Humbertxx)"}

