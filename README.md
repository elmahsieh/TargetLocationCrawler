# TargetLocationCrawler

This is a simple Python-based web scraper designed to extract information about Target stores across various states and cities in the United States. The script fetches data from Target's store locator website and compiles detailed store information (such as name, address, latitude, longitude, phone number, and store type) into a CSV file.

## Features

- Scrapes store information by state and city.
- Handles cities with multiple Target stores by reconstructing URLs based on city names and store IDs.
- Saves the store data to a CSV file with detailed information.
- Avoids using JavaScript-based tools like Selenium by directly fetching the necessary URLs.

## Requirements
See `requirements.txt`. To install: 
`pip install requirements.txt`

