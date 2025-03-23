import os
import re
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resources in container
chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
chrome_options.add_argument("--remote-debugging-port=9222")  # Enable remote debugging

# Manually specify the path to ChromeDriver
#chrome_driver_path = "/usr/local/bin/chromedriver"

# Start the WebDriver with the options and the specified ChromeDriver path
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)



# Setup Selenium WebDriver
# service = Service(ChromeDriverManager().install())

# Initialize WebDriver
# driver = webdriver.Chrome(service=service, options=chrome_options)

# Base URL
base_url = "https://www.adultdvdempire.com/all-dvds.html"

# Open the URL
driver.get(base_url)


def extract_movie_details(driver: WebDriver):
    movie_details_list = []
    
    # Wait for product cards to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".product-card"))
        )
    except:
        print("No movies found on this page.")
        return []

    product_cards = driver.find_elements(By.CSS_SELECTOR, ".product-card")

    for card in product_cards:
        movie_details = {}

        try:
            movie_details["id"] = card.get_attribute("id").replace("card", "")
        except:
            movie_details["id"] = None

        try:
            title_element = card.find_element(By.CSS_SELECTOR, ".product-details__item-title a")
            movie_details["title"] = title_element.get_attribute("textContent").strip()
        except:
            movie_details["title"] = None

        try:
            poster_element = card.find_element(By.CSS_SELECTOR, ".boxcover-container img")
            movie_details["poster_path"] = poster_element.get_attribute("src")
        except:
            movie_details["poster_path"] = None    

        movie_details_list.append(movie_details)

    return movie_details_list


def go_to_next_page(driver: WebDriver):
    try:
        # Try to find the "Next" button dynamically
        next_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Next"))
        )

        # If the button is found and clickable, click it
        next_button.click()
        time.sleep(5)  # Allow time for the page to load
        return True
    except Exception as e:
        print(f"No more pages or error: {e}")
        return False




def save_movies_to_json(movie_details, page_number):
    """Save movie details to a JSON file inside the 'page/' directory"""
    os.makedirs("page", exist_ok=True)  # Ensure the directory exists
    file_name = f"page/{page_number}.json"
    with open(file_name, "w", encoding="utf-8") as json_file:
        json.dump(movie_details, json_file, indent=4, ensure_ascii=False)
    print(f"Saved {len(movie_details)} movies to {file_name}")


try:
    # Wait for the "ageConfirmationButton" and click it
    age_confirmation_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "ageConfirmationButton"))
    )
    age_confirmation_button.click()
    print("Button clicked successfully.")

    # Sleep for a few seconds to allow the page to load
    time.sleep(5)

    page_number = 1  # Keep track of the page number

    while True:
        # Extract the movie details from the current page
        movie_details = extract_movie_details(driver)

        # Save to JSON file
        save_movies_to_json(movie_details, page_number)

        # Try to go to the next page
        if not go_to_next_page(driver):
            break

        page_number += 1  # Increment the page number

    print(f"Scraping completed. {page_number} pages saved.")

except Exception as e:
    print(f"Error: {e}")

# Keeping the browser open for a short time before closing
print("Waiting before closing browser.")
time.sleep(5)

# Close the browser
driver.quit()
