
import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image

# Initialize sample data
data = pd.DataFrame({
    'Name': [],
    'ELO': [],
    'Rank': [],
    'Battles Missed': [],
    'Placements Remaining': []
})

# Rank thresholds
RANKS = [
    ("bamboo", 0, 999),
    ("serum2", 1000, 1099),
    ("more", 1100, 1199),
    ("plat", 1200, 1299),
    ("nork", 1300, 1399),
    ("headliner", 1400, float('inf'))
]

COLOR_SCORES = {
    'Red': 50,
    'Orange': 25,
    'White': 0,
    'Green': -25,
    'Brown': -50,
    'Winner': 100
}

def get_rank(elo):
    for rank_name, min_elo, max_elo in RANKS:
        if min_elo <= elo <= max_elo:
            return rank_name
    return "Unranked"

def apply_color_score(name, color):
    idx = data[data['Name'] == name].index[0]
    data.at[idx, 'ELO'] += COLOR_SCORES[color]
    data.at[idx, 'Placements Remaining'] = max(0, data.at[idx, 'Placements Remaining'] - 1)
    data.at[idx, 'Rank'] = get_rank(data.at[idx, 'ELO'])
    data.at[idx, 'Battles Missed'] = 0

def apply_rank_decay():
    for idx, row in data.iterrows():
        if row['Battles Missed'] < 2:
            data.at[idx, 'ELO'] -= 25
            data.at[idx, 'Battles Missed'] += 1
            data.at[idx, 'Rank'] = get_rank(data.at[idx, 'ELO'])

def import_from_image(uploaded_file):
    img = Image.open(uploaded_file)
    text = pytesseract.image_to_string(img)
    names = [line.strip() for line in text.split('\n') if line.strip()]
    for name in names:
        if name not in data['Name'].values:
            data.loc[len(data)] = [name, 1000, get_rank(1000), 0, 2]

def import_from_csv(uploaded_file):
    imported_data = pd.read_csv(uploaded_file)
    global data
    data = imported_data

# UI Setup
st.set_page_config(page_title="Beat Battle ELO Manager", layout="wide", page_icon="🎚️")
st.markdown("""
    <style>
    .main {
        background-color: #121212;
        color: white;
    }
    .stButton>button {
        background-color: #333;
        color: white;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.image("https://oaidalleapiprodscus.blob.core.windows.net/private/org-YrPMpWEnTsoqU2T1CdM4dKcs/user-0s3kR3jEEknAYlYBum9EScRb/img-NGjAeq769ELq8zUYdVJ6qSm8.png", use_column_width=True)

st.title("SEASON 0 - INIT PRESET (OPEN BETA)")

# Tabs
tabs = st.tabs(["Leaderboard", "Admin Panel"])

# Leaderboard (Public)
with tabs[0]:
    st.header("Leaderboard")
    leaderboard_data = data.sort_values(by="ELO", ascending=False)[['Name', 'ELO', 'Rank']]
    st.table(leaderboard_data)

# Admin Panel (Private)
with tabs[1]:
    st.header("Admin Panel (Private)")
    password = st.text_input("Enter Admin Password", type="password")
    if password == "admin123":  # Change this to a secure password

        st.subheader("Upload Battle Results")
        battle_participants = st.multiselect("Select Participants in this Battle", data['Name'])
        st.write("Assign Scores")
        for name in battle_participants:
            color = st.selectbox(f"Score for {name}", options=list(COLOR_SCORES.keys()), key=name)
            if st.button(f"Apply {color} to {name}", key=name+"_btn"):
                apply_color_score(name, color)
                st.success(f"Applied {color} score to {name}")

        if st.button("Process Rank Decay"):
            apply_rank_decay()
            st.success("Rank decay applied to non-participants")

        st.subheader("Import from CSV")
        uploaded_csv = st.file_uploader("Upload CSV", type="csv")
        if uploaded_csv:
            import_from_csv(uploaded_csv)
            st.success("CSV data imported")

        st.subheader("Import Names from Image")
        uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
        if uploaded_image:
            import_from_image(uploaded_image)
            st.success("Names imported from image")

        if st.button("Download Updated ELO Data"):
            st.download_button("Download CSV", data=data.to_csv(index=False), file_name="elo_data.csv", mime="text/csv")
    else:
        st.warning("Enter a valid admin password to access this panel.")
