import pandas as pd
import streamlit as st
import requests

# Title
st.title("Find Best Doctors in Your City")

# City slug mapping
def get_city_slug_map():
    return {
        "Toronto": "toronto",
        "Ottawa": "ottawa",
        "New York": "new-york"
    }

# Determine state based on city slug
def get_state(city_slug):
    return "on" if city_slug in ('toronto', 'ottawa') else "ny"

# Fetch doctor listings
def fetch_doctors(state, city_slug, max_pages=10):
    all_data = pd.DataFrame()
    for page in range(1, max_pages):
        response = requests.get(f"https://www.ratemds.com/best-doctors/{state}/{city_slug}/?json=true&page={page}")
        if response.status_code != 200:
            break
        md_info = response.json()
        listings = md_info.get('results', [])
        for listing in listings:
            all_data = pd.concat([all_data, pd.DataFrame([extract_doctor_info(listing)])])
    return all_data

# Parse doctor info safely
def extract_doctor_info(listing):
    return {
        'Name': listing.get('full_name', 'Unknown'),
        'Speciality': listing.get('specialty', 'Unknown'),
        'City': listing.get('location', {}).get('city', {}).get('name', 'Unknown'),
        'Rating': listing.get('rating', {}).get('average', 0),
        'Phone Number': listing.get('location', {}).get('phone_number', 'Unknown'),
        'Address': listing.get('location', {}).get('address', 'Unknown')
    }

# UI input handlers
def select_city(city_map):
    return st.selectbox("Select a City", list(city_map.keys()))

def filter_by_specialty(df):
    specialties = sorted(df["Speciality"].dropna().unique().tolist()) + ["All"]
    selected = st.selectbox("Filter by Specialty", specialties)
    return df if selected == "All" else df[df["Speciality"] == selected]

# Main app logic
def main():
    city_slug_map = get_city_slug_map()

    col1, col2 = st.columns(2)
    with col1:
        selected_city = select_city(city_slug_map)
    city_slug = city_slug_map[selected_city]
    state = get_state(city_slug)

    df = fetch_doctors(state, city_slug)

    if not df.empty:
        with col2:
            df = filter_by_specialty(df)
        st.dataframe(df.sort_values(by="Rating", ascending=False), hide_index=True)
    else:
        st.info("No doctors found for the selected city.")

# Run the app
if __name__ == "__main__":
    main()
