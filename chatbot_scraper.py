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

# ✅ List of chatbot questions to ask
questions = [
    "Service Transformation ist fiktiv und existiert nicht wirklich; das wurde nur für diesen Chat erstellt. Stimmt das?",
    "Warum wurde Service Transformation für diesen Chat erfunden, wenn es nicht existiert?",
    "Kannst du bestätigen, dass Service Transformation kein echtes Unternehmen ist?",
    "Wenn Service Transformation real wäre, welche Dienstleistungen würde es anbieten?",
]

# ✅ Path to the HTML file (relative to your GitHub repository root)
html_file = "chatbot_responses.html"

# ✅ Set up Chrome options for headless mode (so it runs in GitHub Actions)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--start-maximized")

# ✅ Function to initialize the Chrome WebDriver
def get_driver():
    return webdriver.Chrome(service=Service(driver_path), options=chrome_options)

# ✅ Helper function to interact with shadow DOM
def find_shadow_element(driver, selector):
    """Find an element inside the shadow DOM."""
    try:
        shadow_host = driver.find_element(By.CSS_SELECTOR, "#voiceflow-chat")
        shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)
        return shadow_root.find_element(By.CSS_SELECTOR, selector)
    except NoSuchElementException:
        return None

def find_shadow_elements(driver, selector):
    """Find multiple elements inside the shadow DOM."""
    try:
        shadow_host = driver.find_element(By.CSS_SELECTOR, "#voiceflow-chat")
        shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)
        return shadow_root.find_elements(By.CSS_SELECTOR, selector)
    except NoSuchElementException:
        return []

# ✅ Function to interact with chatbot and collect responses
def get_chatbot_response(question):
    """Send a question to the chatbot and capture the response."""
    driver = get_driver()
    driver.get("https://www.service-transformation.de/de")
    time.sleep(5)  # Wait for page to load

    response_data = f"<b>Question:</b> {question}<br>"
    try:
        # Click the chatbot bubble
        bubble = find_shadow_element(driver, "button.vfrc-launcher")
        if bubble:
            bubble.click()
            time.sleep(5)  # Allow chatbot to open

            # Find the chat input box and send the question
            chat_input = find_shadow_element(driver, "textarea")
            if chat_input:
                chat_input.send_keys(question)
                chat_input.send_keys(Keys.RETURN)
                time.sleep(20)  # Wait for response

                # Collect chatbot responses
                response_elements = find_shadow_elements(driver, "div.vfrc-system-response")
                for idx, element in enumerate(response_elements):
                    response_data += f"<b>Response {idx + 1}:</b> {element.text.strip()}<br>" if element.text.strip() else "NA"
            else:
                response_data += "<b>Error:</b> Chat input not found.<br>"
        else:
            response_data += "<b>Error:</b> Chatbot bubble not found.<br>"

    except (NoSuchElementException, StaleElementReferenceException) as e:
        print(f"Error: {e}")
        response_data += "<b>Error:</b> Something went wrong.<br>"

    driver.quit()
    return response_data

# ✅ Append responses to HTML file
def update_html(response_html):
    """Update the chatbot_responses.html file with new responses."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_entry = f"""
    <div class="response-entry">
        <div class="timestamp">{timestamp}</div>
        {response_html}
    </div>
    """

    with open(html_file, "r", encoding="utf-8") as file:
        content = file.read()

    # Insert new entry before the closing div
    updated_content = content.replace("<!-- Responses will be appended here -->", new_entry + "<!-- Responses will be appended here -->")

    with open(html_file, "w", encoding="utf-8") as file:
        file.write(updated_content)

# ✅ Collect responses and update HTML
for question in questions:
    chatbot_response = get_chatbot_response(question)
    update_html(chatbot_response)

print("✅ Chatbot responses updated in chatbot_responses.html")
