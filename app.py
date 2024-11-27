from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import sqlitecloud
import streamlit as st
import os

import google.generativeai as genai

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# For generating SQL queries from user input using gemini api
def get_gemini_response(question, prompt):
  model = genai.GenerativeModel('gemini-pro')
  response = model.generate_content([prompt, question])
  return response.text

# Function to retrieve query form database
def read_sql_query(sql,db):
  sqlitecloud_connection_string = db
  conn = sqlitecloud.connect(sqlitecloud_connection_string)
  result = pd.read_sql_query(sql, conn)
  conn.commit()
  conn.close()
  return result

# Defining prompt
prompt = """
    You are an expert in converting English questions to SQL query!\n
    \t\tthis sqlite database has 6 tables, companies, industry_categories, company_industries, products_services, company_products_services, and social_media_profiles.\n
    \t\teach of the table's schema example queries given below\n
    \t\ttable 1 - companies:\n
      \t\tcompanies (\n
          \t\t\tid INTEGER PRIMARY KEY,\n
          \t\t\tname TEXT NOT NULL,\n
          \t\t\twebsite_url TEXT,\n
          \t\t\tphysical_address TEXT,\n
          \t\t\temail TEXT,\n
          \t\t\tcontact_number TEXT,\n
          \t\t\tprofile_description TEXT\n
    \t\t)\n

    \t\tExample query for table companies:\n 
    \t\tInquiry 1: "List all company names and their websites."\n
    \t\tcorresponding sql: SELECT name, website_url FROM companies;\n

    \t\tInquiry 2: "Get the contact details of the company named 'Tech Innovators'."\n
    \t\tcorresponding sql: SELECT contact_number, email FROM companies WHERE name = 'Tech Innovators';\n

    \t\tInquiry 3: "Provide the contact details of companies located in 'Germany'"\n
    \t\tcorresponding sql: SELECT name AS company_name, email, contact_number, physical_address 
    FROM companies
    WHERE physical_address LIKE '%Germany%';\n\n




    \t\ttable 2 - industry_categories:\n
    \t\tindustry_categories (\n
        \t\t\tid INTEGER PRIMARY KEY,\n
        \t\t\tcategory_name TEXT NOT NULL UNIQUE\n
    \t\t)\n

    \t\tExample query for table industry_categories:\n
    \t\tInquiry 1: "What are the names of all industries listed in the database?"\n
    \t\tcorresponding sql: SELECT category_name FROM industry_categories;\n

    \t\tInquiry 2: "How many industries are listed in the database?"\n
    \t\tcorresponding sql: SELECT COUNT(*) FROM industry_categories;\n\n



    \t\ttable 3 - company_industries:\n
    \t\tcompany_industries (\n
        \t\t\tcompany_id INTEGER,\n
        \t\t\tindustry_id INTEGER,\n
        \t\t\tPRIMARY KEY (company_id, industry_id),\n
        \t\t\tFOREIGN KEY (company_id) REFERENCES companies(id),\n
        \t\t\tFOREIGN KEY (industry_id) REFERENCES industry_categories(id)\n
    \t\t)\n

    \t\tExample query for table company_industries:\n
    \t\tInquiry 1: "Which companies belong to the 'Software Development' industry?"\n
    \t\tcorresponding sql: SELECT companies.name
    FROM companies
    JOIN company_industries ON companies.id = company_industries.company_id
    JOIN industry_categories ON company_industries.industry_id = industry_categories.id
    WHERE industry_categories.category_name LIKE '%Software Development%';\n

    \t\tInquiry 2: "Count the number of companies listed under the 'Hardware' industry."\n
    \t\tcorresponding sql: SELECT COUNT(*)
    FROM company_industries 
    JOIN industry_categories ON company_industries.industry_id = industry_categories.id 
    WHERE industry_categories.category_name LIKE '%Hardware%';\n\n



    \t\ttable 4 - products_services:\n
    \t\tproducts_services (\n
        \t\t\tid INTEGER PRIMARY KEY,\n
        \t\t\tproduct_service_name TEXT NOT NULL UNIQUE\n
    \t\t)\n

    \t\tExample query for table products_services:\n
    \t\tInquiry 1: "List all the products or services offered by companies."\n
    \t\tcorresponding sql: SELECT product_service_name FROM products_services;\n

    \t\tInquiry 2: "Find the ID of the product or service 'Cloud Hosting'."\n
    \t\tcorresponding sql: SELECT id FROM products_services WHERE product_service_name LIKW '%Cloud Hosting%';\n\n



    \t\ttable 5 - company_products_services:\n
    \t\tcompany_products_services (\n
        \t\t\tcompany_id INTEGER,\n
        \t\t\tproduct_service_id INTEGER,\n
        \t\t\tPRIMARY KEY (company_id, product_service_id),\n
        \t\t\tFOREIGN KEY (company_id) REFERENCES companies(id),\n
        \t\t\tFOREIGN KEY (product_service_id) REFERENCES products_services(id)\n
    \t\t)\n

    \t\tExample query for table company_products_services:\n
    \t\tInquiry 1: "Which companies offer 'AI Solutions'?"\n
    \t\tcorresponding sql: SELECT companies.name 
    FROM companies 
    JOIN company_products_services ON companies.id = company_products_services.company_id 
    JOIN products_services ON company_products_services.product_service_id = products_services.id 
    WHERE products_services.product_service_name LIKE '%AI Solutions%';\n

    \t\tInquiry 2: "Count how many companies provide 'Web Development' services."\n
    \t\tcorresponding sql: SELECT COUNT(*) 
    FROM company_products_services 
    JOIN products_services ON company_products_services.product_service_id = products_services.id 
    WHERE products_services.product_service_name LIKE '%Web Development%';\n\n




    \t\ttable 6 - social_media_profiles:\n
    \t\tsocial_media_profiles (\n
        \t\t\tid INTEGER PRIMARY KEY,\n
        \t\t\tcompany_id INTEGER,\n
        \t\t\tplatform TEXT NOT NULL,\n
        \t\t\tprofile_url TEXT,\n
        \t\t\tFOREIGN KEY (company_id) REFERENCES companies(id)\n
    \t\t)\n

    \t\tExample query for table social_media_profiles:\n
    \t\tInquiry 1: "List the social media profiles of 'Tech Innovators'."\n
    \t\tcorresponding sql: SELECT platform, profile_url 
    FROM social_media_profiles 
    JOIN companies ON social_media_profiles.company_id = companies.id 
    WHERE companies.name = 'Tech Innovators';\n

    \t\tInquiry 2: "Which companies have a LinkedIn profile?"\n
    \t\tcorresponding sql: SELECT companies.name 
    FROM companies 
    JOIN social_media_profiles ON companies.id = social_media_profiles.company_id 
    WHERE social_media_profiles.platform = 'LinkedIn';\n

    also sql code should not have ``` in the beginning or end and the sql word in the output

"""

# Streamlit UI
st.set_page_config(page_title = "Cavli Wireless")
st.title("Cavli Wireless - Technical Task - 2 (SQL DB interaction Chatbot)")


if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if input := st.chat_input():
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(input)
        response = get_gemini_response(input, prompt)
        data = read_sql_query(response, 'sqlitecloud://cpe9a1u7hk.sqlite.cloud:8860/electronica_data.db?apikey='+ os.getenv('SQLITE_CLOUD'))

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": input})

    # Display bot response
    with st.chat_message("assistant"):
        st.dataframe(data)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": data})



