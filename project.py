import json
import os
import streamlit as st
from scholarly import scholarly
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Create or load the existing JSON file
json_file_name = "author_data.json"

if not os.path.exists(json_file_name):
    # Create an empty JSON file if it doesn't exist
    with open(json_file_name, 'w') as json_file:
        json.dump([], json_file)

with open(json_file_name, 'r') as json_file:
    existing_data = json.load(json_file)

# Function to search for and append author data
def get_author_data(author_name):
    # Search for the author
    search_query = scholarly.search_author(author_name)
    first_author_result = next(search_query)

    # Fill author information
    author = scholarly.fill(first_author_result)

    # Get all publications
    publications = author['publications']

    # Initialize a list to store publication data
    all_publications = []

    # Extract and store publication details
    for publication in publications:
        publication_data = scholarly.fill(publication)
        all_publications.append(publication_data)

    # Append author data to the existing data
    author_data = {
        'author': author,
        'publications': all_publications,
    }
    existing_data.append(author_data)
    existing_data.append({})

    # Save author data to the JSON file
    with open(json_file_name, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)

    # Print the added author's name
    author_name_added = author_data['author']['name']
    st.info(f"Added data for: {author_name_added}")

def clean_json_file(input_file, output_file):
    with open(input_file, 'r') as json_file:
        existing_data = json.load(json_file)

    cleaned_data = []
    for author_data in existing_data:
        author_data.pop('publications', None)
        author = author_data.get('author', {})
        if author:
            # Remove keys from the 'author' section
            keys_to_remove_author = ['container_type', 'url_picture', 'filled', 'source', 'interests', 'organization','public_access']
            author = {key: value for key, value in author.items() if key not in keys_to_remove_author}

            author.pop('coauthors', None)

            # Remove keys from 'publications' inside the 'author' section
            publications = author.get('publications', [])
            cleaned_publications = []
            for publication in publications:
                # Remove keys from the 'bib' section within each publication
                bib = publication.get('bib', {})
                if bib:
                    keys_to_remove_bib = ['pages', 'citation', 'volume', 'number', 'abstract']  # Define keys to remove from 'bib'
                    bib = {key: value for key, value in bib.items() if key not in keys_to_remove_bib}
                    publication['bib'] = bib

                # Remove keys from other sections within 'publications'
                keys_to_remove_publication = ['container_type', 'filled', 'source', 'author_pub_id', 'citedby_url', 'cites_id', 'url_related_articles','cites_per_year','citedby','citedby5y']
                publication = {key: value for key, value in publication.items() if key not in keys_to_remove_publication}
                cleaned_publications.append(publication)

            author['publications'] = cleaned_publications
            author_data['author'] = author

        cleaned_data.append(author_data)

    with open(output_file, 'w') as cleaned_json_file:
        json.dump(cleaned_data, cleaned_json_file, indent=4)

output_json_file = "cleaned_output.json" 

clean_json_file(json_file_name, output_json_file)

# Streamlit front end
st.title("Research Publications Management System")

# List of author names
author_names = ['Prasad Honnavalli', 'Adithya Balasubramanyam', 'Ashok Kumar Patil',
                'Nagasundari S, Ph.D. IEEE Member, ASRG Member', 'Preet Kanwal PES',
                'Dr. Roopa Ravish', 'Charanraj B R', 'Pavan A C PES',
                'revathi gp', 'Vadiraja Acharya', 'Dr. Sapna V M', 'Radhika MN PES']

# Sort the author names alphabetically
author_names.sort()

# Dropdown to select author
selected_author = st.selectbox("Select an author", author_names)

# Button to generate JSON Data
if st.button("Generate Professor's Data"):
    get_author_data(selected_author)

# Button to convert to Excel
if st.button("Convert to Excel"):
    # Initialize the web driver (Make sure you have the Chrome WebDriver or other supported browser's driver installed).
    driver = webdriver.Chrome()

    # Open the website.
    driver.get("https://products.aspose.app/cells/conversion/json-to-xlsx")

    # Wait for the page to load (you may need to adjust the sleep duration).
    time.sleep(5)

    # Locate the "Choose File" button and send the JSON file.
    upload_input = driver.find_element(By.XPATH, "//input[@type='file']")
    upload_input.send_keys(os.path.abspath(output_json_file))

    # Locate and click the "Convert" button.
    convert_button = driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div[2]/div/div/div[1]/form/div[3]/div[2]/input")
    convert_button.click()

    # Wait for the conversion to complete (you may need to adjust the sleep duration).
    time.sleep(10)  # You can increase this duration if needed.

    # Locate and click the "Download" button after waiting for the modal to disappear.
    wait = WebDriverWait(driver, 10)
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "modal-backdrop")))
    download_button = driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div[2]/div/div/div[2]/div[2]/span/a")
    download_button.click()

    # Wait for the download to complete (you may need to adjust the sleep duration).
    time.sleep(5)

    # Close the web browser.
    driver.quit()

    st.success("Downloaded the XLSX file from the website.")

import pandas as pd
import json

# Load the cleaned JSON file
with open('cleaned_output.json', 'r') as file:
    data = json.load(file)

# Separate data into three categories: professors, citations, and publications
professors_data = []
citations_data = []
publications_data = []

for item in data:
    author = item.get('author', {})
    publications = author.get('publications', [])

    professors_data.append({
        'scholar_id': author.get('scholar_id', ''),
        'name': author.get('name', ''),
        'affiliation': author.get('affiliation', ''),
        'email_domain': author.get('email_domain', '')
    })

    for pub in publications:
        citations_data.append({
            'scholar_id': author.get('scholar_id', ''),
            'citedby': author.get('citedby', ''),
            'citedby5y': author.get('citedby5y', ''),
            'hindex': author.get('hindex', ''),
            'hindex5y': author.get('hindex5y', ''),
            'i10index': author.get('i10index', ''),
            'i10index5y': author.get('i10index5y', ''),
            'cites_per_year_2023': author.get('cites_per_year', {}).get('2023', ''),
            'cites_per_year_2022': author.get('cites_per_year', {}).get('2022', ''),
            'cites_per_year_2021': author.get('cites_per_year', {}).get('2021', ''),
            'cites_per_year_2020': author.get('cites_per_year', {}).get('2020', ''),
            'cites_per_year_2019': author.get('cites_per_year', {}).get('2019', ''),
            'cites_per_year_2018': author.get('cites_per_year', {}).get('2018', ''),
            'cites_per_year_2017': author.get('cites_per_year', {}).get('2017', ''),
            'cites_per_year_2016': author.get('cites_per_year', {}).get('2016', ''),
            'cites_per_year_2015': author.get('cites_per_year', {}).get('2015', ''),
            'cites_per_year_2014': author.get('cites_per_year', {}).get('2014', ''),

        })

        publications_data.append({
            'scholar_id': author.get('scholar_id', ''),
            'title': pub.get('bib', {}).get('title', ''),
            'pub_year': pub.get('bib', {}).get('pub_year', ''),
            'author': pub.get('bib', {}).get('author', ''),
            'journal': pub.get('bib', {}).get('journal', ''),
            'publisher': pub.get('bib', {}).get('publisher', ''),
            'conference': pub.get('bib', {}).get('conference', ''),
            'num_citations': pub.get('num_citations', ''),
            'pub_url': pub.get('pub_url', ''),
        })

# Create DataFrames for each category
professors_df = pd.DataFrame(professors_data)
citations_df = pd.DataFrame(citations_data)
publications_df = pd.DataFrame(publications_data)

# Write DataFrames to separate Excel files
professors_df.to_excel('professors.xlsx', index=False)
citations_df.to_excel('citations.xlsx', index=False)
publications_df.to_excel('publications.xlsx', index=False)
