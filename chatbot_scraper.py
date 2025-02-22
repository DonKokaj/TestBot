import os
import time
import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

# Outlook SMTP Configuration
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587

# Load sender credentials from GitHub Secrets
SENDER_EMAIL = os.getenv("EMAIL_USERNAME")  # Sender's Outlook email
SENDER_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Outlook password (use App Password if needed)

# Specify recipients directly in the script
RECIPIENT_EMAILS = ["recipient1@example.com", "recipient2@example.com"]  # Add multiple if needed

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

# Function to initialize the Chrome WebDriver
def get_driver():
    return webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=chrome_options)

# Helper function to interact with shadow DOM
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

# Function to interact with chatbot and collect responses
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

# Collect responses
for question in questions:
    responses.append(get_chatbot_response(question))

# Function to send email via Outlook
def send_email(responses):
    """Sends the chatbot responses via Outlook email."""
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = ", ".join(RECIPIENT_EMAILS)
        msg['Subject'] = "Chatbot Responses"

        # Create HTML content
        html_content = "<h2>Chatbot Responses</h2>"
        html_content += "<br>".join(responses)

        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))

        # Send email using Outlook SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAILS, msg.as_string())
        server.quit()
        
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# Send chatbot responses via email
send_email(responses)
