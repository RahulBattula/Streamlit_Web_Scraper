import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(
    page_title="Table Scraper",
    page_icon="https://img.icons8.com/?size=100&id=ITIhejPZQD5g&format=png&color=000000"
)

def scrape_tables(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None, f"Failed to retrieve content. Status code: {response.status_code}"

    soup = BeautifulSoup(response.content, 'html.parser')
    tables = soup.find_all('table')
    if not tables:
        return None, "No tables found on the page."

    dataframes = []
    sections = []

    for idx, table in enumerate(tables):
        rows = table.find_all('tr')
        data = []
        for row in rows:
            cols = row.find_all(['td', 'th'])
            cols = [ele.get_text(strip=True) for ele in cols]
            data.append(cols)
        df = pd.DataFrame(data)
        dataframes.append(df)
        # Try to get section heading or use default name if not available
        section_title = table.find_previous(['h3', 'h2', 'h1'])  # Adjust header tags if needed
        sections.append(section_title.get_text(strip=True) if section_title else f"Table {idx + 1}")

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

    if st.button("Get Tables"):
        if url:
            sections, dataframes = scrape_tables(url)
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
