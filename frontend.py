import mysql.connector
import streamlit as st
import pandas as pd

# Establish MySQL connection without specifying database initially
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password=''
)
cursor = conn.cursor()

# Create the database if it doesn't exist
cursor.execute("CREATE DATABASE IF NOT EXISTS dbms_project")

# Switch to the 'dbms_project' database
conn.database = 'dbms_project'

# Create Professors, Citations, and Publications tables (if not exist)
cursor.execute('''CREATE TABLE IF NOT EXISTS professors (
                    scholar_id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255),
                    affiliation VARCHAR(255),
                    email_domain VARCHAR(255)
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS citations (
                    scholar_id VARCHAR(255),
                    citedby INT,
                    citedby5y INT,
                    hindex INT,
                    hindex5y INT,
                    i10index INT,
                    i10index5y INT,
                    cites_per_year_2023 VARCHAR(10),
                    cites_per_year_2022 VARCHAR(10),
                    cites_per_year_2021 VARCHAR(10),
                    cites_per_year_2020 VARCHAR(10),
                    cites_per_year_2019 VARCHAR(10),
                    cites_per_year_2018 VARCHAR(10),
                    cites_per_year_2017 VARCHAR(10),
                    cites_per_year_2016 VARCHAR(10),
                    cites_per_year_2015 VARCHAR(10),
                    cites_per_year_2014 VARCHAR(10),
                    FOREIGN KEY (scholar_id) REFERENCES professors(scholar_id)
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS publications (
                    scholar_id VARCHAR(255),
                    title TEXT,
                    pub_year VARCHAR(4),
                    author TEXT,
                    journal TEXT,
                    publisher TEXT,
                    conference TEXT,
                    num_citations INT,
                    pub_url TEXT,
                    FOREIGN KEY (scholar_id) REFERENCES professors(scholar_id)
                )''')

# Commit changes
conn.commit()

# Read data from Excel files and insert into tables
professors_data = pd.read_excel('professors.xlsx').values.tolist()
citations_data = pd.read_excel('citations.xlsx').values.tolist()
publications_data = pd.read_excel('publications.xlsx').values.tolist()

# Insert data into Professors table
insert_query = "INSERT IGNORE INTO professors (scholar_id, name, affiliation, email_domain) VALUES (%s, %s, %s, %s)"
cursor.executemany(insert_query, professors_data)

# Insert data into Citations table
insert_query = '''INSERT IGNORE INTO citations (scholar_id, citedby, citedby5y, hindex, hindex5y, i10index, i10index5y,
                    cites_per_year_2023, cites_per_year_2022, cites_per_year_2021, cites_per_year_2020, cites_per_year_2019,
                    cites_per_year_2018, cites_per_year_2017, cites_per_year_2016, cites_per_year_2015, cites_per_year_2014)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
cursor.executemany(insert_query, citations_data)

# Insert data into Publications table
insert_query = '''INSERT IGNORE INTO publications (scholar_id, title, pub_year, author, journal, publisher, conference,
                    num_citations, pub_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
cursor.executemany(insert_query, publications_data)

# Commit changes and close connection
conn.commit()
conn.close()

print("Tables created successfully in the 'dbms_project' database and data inserted, handling duplicate entries.")

st.title('Professors Publications Management System')

# Establish MySQL connection to perform queries
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='dbms_project'
)
cursor = conn.cursor()

# Query all professor names from the 'professors' table
cursor.execute("SELECT name FROM professors")
professor_names = [row[0] for row in cursor.fetchall()]

# Remove None values (if any)
professor_names = [name for name in professor_names if name is not None]

# Sort the names in alphabetical order
if professor_names:
    professor_names.sort()
else:
    # Handle the case when no names are retrieved
    st.error("No professor names found.")

# User input: Select a professor from the dropdown
selected_professor = st.selectbox('Select a Professor:', professor_names)
# User input: Select information category
selected_category = st.selectbox('Select a Category:', ['About', 'Citations', 'Publications'])

# Function to retrieve data based on selected professor and category
def retrieve_data(selected_professor, selected_category):
    if selected_category == 'About':
        cursor.execute(f"SELECT * FROM professors WHERE name = '{selected_professor}'")
    elif selected_category == 'Citations':
        cursor.execute(f"SELECT DISTINCT * FROM citations WHERE scholar_id IN (SELECT scholar_id FROM professors WHERE name = '{selected_professor}')")
    elif selected_category == 'Publications':
        cursor.execute(f"SELECT DISTINCT * FROM publications WHERE scholar_id IN (SELECT scholar_id FROM professors WHERE name = '{selected_professor}')")

    result = cursor.fetchall()
    return result

# Display information in tabular format
if st.button('Get Information'):
    result = retrieve_data(selected_professor, selected_category)

    if result:
        st.write(f'{selected_category} for {selected_professor}:')
        if selected_category == 'About':
            df = pd.DataFrame([result[0]], columns=[desc[0] for desc in cursor.description])
        else:
            df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])
        st.write(df)
    else:
        st.write('No information available.')

# Close MySQL connection
conn.close()
