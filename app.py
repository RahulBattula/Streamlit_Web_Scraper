import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import io

def scrape_tables(url, table_class):
    response = requests.get(url)
    if response.status_code != 200:
        return None, f"Failed to retrieve content. Status code: {response.status_code}"

    soup = BeautifulSoup(response.content, 'html.parser')
    tables = soup.find_all('table', class_=table_class)
    if not tables:
        return None, "No tables found with the given class name."

    dataframes = []
    sections = []

    for table in tables:
        rows = table.find_all('tr')
        data = []
        for row in rows:
            cols = row.find_all(['td', 'th'])
            cols = [ele.get_text(strip=True) for ele in cols]
            data.append(cols)
        df = pd.DataFrame(data)
        dataframes.append(df)
        section_title = table.find_previous('h3')
        sections.append(section_title.get_text(strip=True) if section_title else "Table")

    return sections, dataframes

def main():
    logo_url = "https://img.icons8.com/?size=100&id=ITIhejPZQD5g&format=png&color=000000"
    st.markdown(
        f"""
        <div style="display: flex; align-items: center;">
            <img src="{logo_url}" width="50" style="margin-right: 15px;">
            <h1>Web Scraper for Tables</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    url = st.text_input("Enter the website URL")
    table_class = st.text_input("Enter the table's class name")

    if st.button("Scrape Tables"):
        if url and table_class:
            sections, dataframes = scrape_tables(url, table_class)
            if sections is None:
                st.error(dataframes)
            else:
                st.session_state['sections'] = sections
                st.session_state['dataframes'] = dataframes
                st.success(f"Scraped {len(sections)} tables successfully!")

    if 'sections' in st.session_state and 'dataframes' in st.session_state:
        sections = st.session_state['sections']
        dataframes = st.session_state['dataframes']

        st.subheader("Scraped Tables")
        table_index = st.selectbox("Select Table", range(len(sections)), format_func=lambda x: sections[x])

        if st.button("Display Selected Table"):
            st.write(f"Displaying table: {sections[table_index]}")
            st.dataframe(dataframes[table_index].head())

        if st.button("Download Selected Table as CSV"):
            df = dataframes[table_index]
            csv = df.to_csv(index=False)
            st.download_button(label="Download CSV", data=csv, file_name=f"table_{table_index}.csv", mime="text/csv")

if __name__ == "__main__":
    main()
