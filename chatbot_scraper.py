import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

# ✅ Use ChromeDriver path for GitHub Actions
driver_path = "/usr/bin/chromedriver"

# ✅ Path to the HTML file
html_file = "index.html"

# ✅ Ensure index.html exists before writing
def ensure_html_file():
    """Create index.html if it does not exist."""
    if not os.path.exists(html_file):
        print("⚠️ Creating index.html for the first time...")
        with open(html_file, "w", encoding="utf-8") as file:
            file.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot Responses</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f8f9fa;
            margin: 20px;
            padding: 20px;
            text-align: center;
        }
        #responses {
            max-width: 800px;
            margin: auto;
            padding: 20px;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .response-entry {
            border-bottom: 1px solid #ddd;
            padding: 10px;
            margin-bottom: 10px;
            text-align: left;
        }
        .timestamp {
            font-size: 12px;
            color: #777;
        }
    </style>
</head>
<body>

    <h2>Chatbot Responses</h2>
    <div id="responses">
        <!-- Responses will be appended here -->
    </div>

</body>
</html>
            """)

# ✅ Append responses to HTML file
def update_html(response_html):
    """Update index.html with new responses."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_entry = f"""
    <div class="response-entry">
        <div class="timestamp">{timestamp}</div>
        {response_html}
    </div>
    """

    with open(html_file, "r", encoding="utf-8") as file:
        content = file.read()

    if "<!-- Responses will be appended here -->" in content:
        print("✅ Found placeholder in index.html, inserting new response...")
        updated_content = content.replace(
            "<!-- Responses will be appended here -->", 
            new_entry + "<!-- Responses will be appended here -->"
        )
        with open(html_file, "w", encoding="utf-8") as file:
            file.write(updated_content)
        print("✅ index.html successfully updated!")
    else:
        print("❌ ERROR: Placeholder not found in index.html. Skipping update.")

# ✅ Ensure the HTML file exists
ensure_html_file()

# ✅ Example Test: Updating the file manually
test_response = "<b>Test Run:</b> This is a test response added for debugging."
update_html(test_response)

print("✅ Test update completed. Check index.html content.")
