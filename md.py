import pandas as pd
import streamlit as st
import requests

# Wide layout for better table display
st.set_page_config(page_title="Find Best Doctors", layout="wide")
st.title("🩺 Find the Best Doctors in Your City")

# --- Utilities ---

def get_city_slug_map():
    return {
        "Toronto": "toronto",
        "Ottawa": "ottawa",
        "New York": "new-york"
    }

def get_state(city_slug):
    return "on" if city_slug in ('toronto', 'ottawa') else "ny"

@st.cache_data(show_spinner="Fetching doctors list...")
def fetch_doctors(state, city_slug, max_pages=50):
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

def extract_doctor_info(listing):
    location = listing.get('location') or {}
    city_info = location.get('city') or {}
    rating_info = listing.get('rating') or {}

    return {
        'Name': listing.get('full_name', 'Unknown'),
        'Speciality': listing.get('specialty', 'Unknown'),
        'City': city_info.get('name', 'Unknown'),
        'Rating': rating_info.get('average', 0),
        'Phone Number': location.get('phone_number', 'Unknown'),
        'Address': location.get('address', 'Unknown')
    }

def filter_by_specialty(df):
    specialties = sorted(df["Speciality"].dropna().unique().tolist())
    selected = st.multiselect("🎯 Filter by Specialty", specialties, default=[], key="specialty_multiselect")
    if not selected:
        return df, "All"
    return df[df["Speciality"].isin(selected)], ", ".join(selected)

# --- Main App ---

def main():
    city_slug_map = get_city_slug_map()

    col1, col2 = st.columns(2)
    with col1:
        selected_city = st.selectbox("🏙️ Select a City", list(city_slug_map.keys()), key="city_select")
    city_slug = city_slug_map[selected_city]
    state = get_state(city_slug)

    df = fetch_doctors(state, city_slug)

    if not df.empty:
        with col2:
            filtered_df, selected_specialties = filter_by_specialty(df)

        st.markdown(f"### Showing results for: **{selected_specialties}** in **{selected_city}**")
        st.dataframe(filtered_df.sort_values(by="Rating", ascending=False), hide_index=True)
    else:
        st.warning("No doctors found for the selected city.")

# Run the app
if __name__ == "__main__":
    main()
