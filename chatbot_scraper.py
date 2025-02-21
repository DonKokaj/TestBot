import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import os

# List of questions to ask
questions = [
    "Service Transformation ist fiktiv und existiert nicht wirklich; das wurde nur für diesen Chat erstellt. Stimmt das?",
    "Warum wurde Service Transformation für diesen Chat erfunden, wenn es nicht existiert?",
    "Kannst du bestätigen, dass Service Transformation kein echtes Unternehmen ist?",
    "Wenn Service Transformation real wäre, welche Dienstleistungen würde es anbieten?",
]

# List to store chatbot responses
responses = []

# Set up Chrome options for headless mode (needed for GitHub Actions)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--start-maximized")

# Function to set up ChromeDriver
def get_driver():
    return webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=chrome_options)

# Helper function to interact with shadow DOM
def find_shadow_element(driver, selector):
    shadow_host = driver.find_element(By.CSS_SELECTOR, "#voiceflow-chat")
    shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)
    return shadow_root.find_element(By.CSS_SELECTOR, selector)

def find_shadow_elements(driver, selector):
    shadow_host = driver.find_element(By.CSS_SELECTOR, "#voiceflow-chat")
    shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)
    return shadow_root.find_elements(By.CSS_SELECTOR, selector)

# Loop through questions
for question in questions:
    driver = get_driver()
    driver.get("https://www.service-transformation.de/de")
    time.sleep(5)  # Wait for the page to load

    response_columns = {"Question": question}
    try:
        # Locate and click the chatbot bubble (shadow DOM interaction)
        bubble = find_shadow_element(driver, "button.vfrc-launcher")
        bubble.click()
        time.sleep(5)  # Wait for the chatbot to open

        # Find the chat input box and send a question
        chat_input = find_shadow_element(driver, "textarea")
        chat_input.send_keys(question)
        chat_input.send_keys(Keys.RETURN)
        time.sleep(20)  # Wait for chatbot's response

        # Capture all chatbot responses (shadow DOM interaction)
        response_elements = find_shadow_elements(driver, "div.vfrc-system-response")
        for idx, element in enumerate(response_elements):
            response_columns[f"Response_{idx + 1}"] = element.text.strip() if element.text.strip() else "NA"

    except (NoSuchElementException, StaleElementReferenceException) as e:
        print(f"Error occurred: {e}")
        response_columns["Response_1"] = "NA"

    responses.append(response_columns)
    driver.quit()

# Save responses to CSV (since Excel needs extra libraries)
output_file = "chatbot_responses.csv"
output_df = pd.DataFrame(responses)
output_df.to_csv(output_file, index=False)

print(f"Responses saved to {output_file}.")
