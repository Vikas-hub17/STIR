from flask import Flask, jsonify, render_template, send_file
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
from datetime import datetime
import time
import random
import json

app = Flask(__name__)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client['stir_tech']
collection = db['trending_topics']

# ProxyMesh credentials
PROXY_USER = "Vikas"
PROXY_PASS = "ATTU@dec2002"
PROXY_HOST = "us-ca.proxymesh.com"
PROXY_PORT = "31280"

# Shared progress and control variables
progress = {"status": "Idle"}
stop_script = False

def scrape_trends():
    global progress, stop_script
    progress["status"] = "Initializing Selenium"
    stop_script = False  # Reset the stop flag at the start

    # Configure Selenium WebDriver
    proxy = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
    chrome_options = Options()
    chrome_options.add_argument(f"--proxy-server={proxy}")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    service = Service('C:\chromedriver-win64\chromedriver-win64')  # No full path needed
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        progress["status"] = "Logging into Twitter"
        driver.get("https://twitter.com/login")
        time.sleep(2)
        if stop_script: return {"status": "Script Stopped"}

        username = driver.find_element(By.NAME, "text")
        username.send_keys("VIKASRA68478394")
        username.send_keys(Keys.RETURN)
        time.sleep(2)
        if stop_script: return {"status": "Script Stopped"}

        password = driver.find_element(By.NAME, "password")
        password.send_keys("ATTU@dec2002")
        password.send_keys(Keys.RETURN)
        time.sleep(5)
        if stop_script: return {"status": "Script Stopped"}

        progress["status"] = "Scraping trending topics"
        driver.get("https://twitter.com/home")
        time.sleep(5)
        if stop_script: return {"status": "Script Stopped"}

        trends = driver.find_elements(By.XPATH, "//section//span")[:5]
        trend_names = [trend.text for trend in trends if trend.text]

        ip_address = "ProxyMesh IP"
        unique_id = f"trend-{random.randint(1000, 9999)}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data = {
            "_id": unique_id,
            "trend1": trend_names[0] if len(trend_names) > 0 else "N/A",
            "trend2": trend_names[1] if len(trend_names) > 1 else "N/A",
            "trend3": trend_names[2] if len(trend_names) > 2 else "N/A",
            "trend4": trend_names[3] if len(trend_names) > 3 else "N/A",
            "trend5": trend_names[4] if len(trend_names) > 4 else "N/A",
            "timestamp": timestamp,
            "ip_address": ip_address,
        }

        progress["status"] = "Saving results"
        collection.insert_one(data)
        progress["status"] = "Completed"
        return data

    except Exception as e:
        progress["status"] = f"Error: {str(e)}"
        return {"error": str(e)}

    finally:
        driver.quit()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/run-script', methods=['GET'])
def run_script():
    print("Run script endpoint hit!")  # Debug log
    result = scrape_trends()
    print("Result:", result)  # Debug log
    return jsonify(result)

@app.route('/stop-script', methods=['POST'])
def stop_script_route():
    global stop_script
    stop_script = True
    return jsonify({"status": "Stopping script"})


@app.route('/get-progress', methods=['GET'])
def get_progress():
    return jsonify(progress)


if __name__ == '__main__':
    app.run(debug=True)
