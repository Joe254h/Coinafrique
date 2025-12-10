#These are the packages i have used throughout the project
# some of them are new I took time to understand them and use them effectively

import streamlit as st
import pandas as pd
import sqlite3
from requests import get
from bs4 import BeautifulSoup as bs
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time


#this is the title of the project 
st.set_page_config(page_title="CoinAfrique Real Estate", layout="wide", page_icon="🏠")


# DATABASE INITIALIZATION
# here we first create the database so that once we scrape the data for each category we can put it there.

def init_db():
    conn = sqlite3.connect('real_estate.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS villas (
        ad_type TEXT, price TEXT, address TEXT, number_of_rooms TEXT,
        link_image TEXT, scraped_date TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS terrains (
        price TEXT, address TEXT, surface TEXT,
        link_image TEXT, scraped_date TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS appartements (
        price TEXT, address TEXT, number_of_rooms TEXT,
        link_image TEXT, scraped_date TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS villas_cleaned (
        id INTEGER PRIMARY KEY AUTOINCREMENT, ad_type TEXT, price REAL,
        address TEXT, number_of_rooms INTEGER, link_image TEXT, scraped_date TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS terrains_cleaned (
        id INTEGER PRIMARY KEY AUTOINCREMENT, price REAL, address TEXT,
        surface REAL, link_image TEXT, scraped_date TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS appartements_cleaned (
        id INTEGER PRIMARY KEY AUTOINCREMENT, price REAL, address TEXT,
        number_of_rooms INTEGER, link_image TEXT, scraped_date TEXT
    )''')

    conn.commit()
    conn.close()


# SCRAPERS
# here we start by scarping data in for villas
def scrape_villas(max_pages=5, progress_bar=None):
    df = pd.DataFrame()
    scraped_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #here we set the indexing to allow us run through different pages 
    for index in range(1, max_pages + 1):
        if progress_bar:
            progress_bar.progress(index / max_pages)

        url = f'https://sn.coinafrique.com/categorie/villas?page={index}'
        try:
            res = get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            soup = bs(res.text, "html.parser")
            containers = soup.find_all("div", class_="col s6 m4 l3") #containers setting
            data = []

            for container in containers:
                try:
                    relative_link = container.find("a", class_="card-image")["href"]
                    detail_url = "https://sn.coinafrique.com" + relative_link
                    ad_type = relative_link.split("/")[2]

                    raw_price = container.find("p", class_="ad__card-price").text.strip()
                    price = None if "Prix" in raw_price else raw_price.replace("CFA", "").replace(" ", "")

                    address = container.find("p", class_="ad__card-location").find("span").text.strip()
                    link_image = container.find("img", class_="ad__card-img")["src"]

                    res_detail = get(detail_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                    soup_detail = bs(res_detail.text, "html.parser")

                    rooms_tag = soup_detail.find("img", src=lambda x: x and "Icon_Pieces" in x)
                    number_of_rooms = rooms_tag.find_parent("li").find("span", class_="qt").text.strip() if rooms_tag else None

                    data.append({
                        "ad_type": ad_type, "price": price, "address": address,
                        "number_of_rooms": number_of_rooms, "link_image": link_image,
                        "scraped_date": scraped_date
                    })
                except:
                    pass

            df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
            time.sleep(1)
        except:
            pass

    return df

# here we scrape data for terrains 
def scrape_terrains(max_pages=5, progress_bar=None):
    df = pd.DataFrame()
    scraped_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #we set the indexing to allow us go through the pages and different containers 
    for index in range(1, max_pages + 1):
        if progress_bar:
            progress_bar.progress(index / max_pages)

        url = f'https://sn.coinafrique.com/categorie/terrains?page={index}'
        try:
            res = get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            soup = bs(res.text, "html.parser")
            containers = soup.find_all("div", class_="col s6 m4 l3")
            data = []

            for container in containers:
                try:
                    detail_url = "https://sn.coinafrique.com" + container.find("a")["href"]
                    raw_price = container.find("p", class_="ad__card-price").text.strip()
                    price = None if "Prix" in raw_price else raw_price.replace("CFA", "").replace(" ", "")
                    address = container.find("p", class_="ad__card-location").find("span").text.strip()
                    link_image = container.find("img", class_="ad__card-img")["src"]

                    res_detail = get(detail_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                    soup_detail = bs(res_detail.text, "html.parser")

                    surface_tag = soup_detail.find("img", src=lambda x: x and "Icon_Superficie" in x)
                    surface = None
                    if surface_tag:
                        raw_surface = surface_tag.find_parent("li").find("span", class_="qt").text.strip()
                        surface = raw_surface.replace("m2", "").replace("m²", "").replace(" ", "")

                    data.append({
                        "price": price, "address": address, "surface": surface,
                        "link_image": link_image, "scraped_date": scraped_date
                    })
                except:
                    pass

            df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
            time.sleep(1)
        except:
            pass

    return df

#here we scrape data for appartments 
def scrape_appartements(max_pages=5, progress_bar=None):
    df = pd.DataFrame()
    scraped_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #we set the indexing to allow us scrape data from different pages and also containers 
    for index in range(1, max_pages + 1):
        #this is the progress bar  to show us if the scraper has finished the scraping
        if progress_bar:
            progress_bar.progress(index / max_pages)
        #url
        url = f'https://sn.coinafrique.com/categorie/appartements?page={index}'
        try:
            res = get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            soup = bs(res.text, "html.parser")
            containers = soup.find_all("div", class_="col s6 m4 l3")
            data = []

            for container in containers:
                try:
                    detail_url = "https://sn.coinafrique.com" + container.find("a")["href"]
                    raw_price = container.find("p", class_="ad__card-price").text.strip()
                    price = None if "Prix" in raw_price else raw_price.replace("CFA", "").replace(" ", "")
                    address = container.find("p", class_="ad__card-location").find("span").text.strip()
                    link_image = container.find("img", class_="ad__card-img")["src"]

                    res_detail = get(detail_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                    soup_detail = bs(res_detail.text, "html.parser")

                    rooms_tag = soup_detail.find("img", src=lambda x: x and "Icon_Pieces" in x)
                    number_of_rooms = rooms_tag.find_parent("li").find("span", class_="qt").text.strip() if rooms_tag else None

                    data.append({
                        "price": price, "address": address, "number_of_rooms": number_of_rooms,
                        "link_image": link_image, "scraped_date": scraped_date
                    })
                except:
                    pass

            df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
            time.sleep(1)
        except:
            pass

    return df


# DATA CLEANING
# After collecting data we need to clean and below is a systematic way of doing that so that we can download clean data 

def clean_villas_data(df):
    df_clean = df.copy()
    #here we change price to interger and also replace the , with empty also . with empty
    # And again we change the number of rooms into intergers too and
    #And for all we drop null
    df_clean['price'] = pd.to_numeric(df_clean['price'].str.replace(",", "").str.replace(".", ""), errors='coerce')
    df_clean['number_of_rooms'] = pd.to_numeric(df_clean['number_of_rooms'], errors='coerce').fillna(0).astype(int)
    return df_clean.dropna(subset=['price'])


def clean_terrains_data(df):
    #here we change price to interger and also replace the , with empty also . with empty
    #we convert surface to float numbers
    #then we drop null for all 
    df_clean = df.copy()
    df_clean['price'] = pd.to_numeric(df_clean['price'].str.replace(",", "").str.replace(".", ""), errors='coerce')
    df_clean['surface'] = pd.to_numeric(df_clean['surface'], errors='coerce')
    return df_clean.dropna(subset=['price'])


def clean_appartements_data(df):
    #here we change price to interger and also replace the , with empty also . with empty
    # And again we change the number of rooms into intergers too and
    #And for all we drop null
    df_clean = df.copy()
    df_clean['price'] = pd.to_numeric(df_clean['price'].str.replace(",", "").str.replace(".", ""), errors='coerce')
    df_clean['number_of_rooms'] = pd.to_numeric(df_clean['number_of_rooms'], errors='coerce').fillna(0).astype(int)
    return df_clean.dropna(subset=['price'])


# DATABASE OPERATIONS
# after scraping the data we now load it to the database so that we can be able
#  to see all the other things we need from clean data 

def save_to_db(df, table_name):
    conn = sqlite3.connect("real_estate.db")
    df.to_sql(table_name, conn, if_exists="append", index=False)
    conn.close()

def load_from_db(table_name):
    conn = sqlite3.connect("real_estate.db")
    try:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

init_db()


# THEME SYSTEM
#giving the web application a good them is important
# this enables easy visualization since there is the option of either dark or light so depending on someone preference
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def apply_theme():
    if st.session_state.theme == 'dark':
        st.markdown("""<style>
        .main{background-color:#0E1117;color:#FAFAFA}
        .stButton>button{
            background:linear-gradient(135deg,#FF6934 0%,#FF4500 100%);
            color:white;font-weight:600;border-radius:10px;padding:18px;
            border:none;font-size:16px;width:100%;
            box-shadow:0 4px 12px rgba(255,105,52,0.3);
            transition:all 0.3s ease
        }
        .stButton>button:hover{
            transform:translateY(-2px);
            box-shadow:0 6px 20px rgba(255,105,52,0.5)
        }
        .category-card{
            background:linear-gradient(135deg,#1C1C1C 0%,#2D2D2D 100%);
            padding:25px;border-radius:12px;text-align:center;
            color:#FAFAFA;box-shadow:0 4px 15px rgba(0,0,0,0.3);
            margin:10px 0;border:2px solid #FF6934
        }
        .property-image{
            width:100%;height:200px;object-fit:cover;
            border-radius:8px;margin-bottom:15px;
            border:2px solid #FF6934
        }
        section[data-testid="stSidebar"]{background-color:#1C1C1C}
        .stMetric{background:#1C1C1C;padding:15px;border-radius:8px;border:1px solid #FF6934}
        .stMetric label{color:#FF6934 !important}
        </style>""", unsafe_allow_html=True)
    else:
        st.markdown("""<style>
        .main{background:linear-gradient(135deg,#F5F7FA 0%,#E8EBF0 100%);color:#1A1A1A}
        .stButton>button{
            background:linear-gradient(135deg,#FF6934 0%,#FF4500 100%);
            color:white;font-weight:600;border-radius:10px;padding:18px;
            border:none;font-size:16px;width:100%;
            box-shadow:0 4px 12px rgba(255,105,52,0.3);
            transition:all 0.3s ease
        }
        .stButton>button:hover{
            transform:translateY(-2px);
            box-shadow:0 6px 20px rgba(255,105,52,0.5)
        }
        .category-card{
            background:linear-gradient(135deg,#FFFFFF 0%,#F8F9FA 100%);
            padding:25px;border-radius:12px;text-align:center;
            color:#1A1A1A;box-shadow:0 4px 15px rgba(0,0,0,0.1);
            margin:10px 0;border:2px solid #FF6934
        }
        .property-image{
            width:100%;height:200px;object-fit:cover;
            border-radius:8px;margin-bottom:15px;
            border:2px solid #FF6934
        }
        section[data-testid="stSidebar"]{background:#FFFFFF}
        .stMetric{background:white;padding:15px;border-radius:8px;border:1px solid #FF6934;box-shadow:0 2px 8px rgba(0,0,0,0.05)}
        .stMetric label{color:#FF6934 !important}
        </style>""", unsafe_allow_html=True)

apply_theme()


# HEADER
# here I decided to choose the header for my application 
# so here we get the logo of coinafrique and insert it in the middle 


col1, col2 = st.columns([9,1])

with col1:
    st.markdown('<div style="text-align:center;padding:20px 0">'
                '<img src="https://static.coinafrique.com/static/images/logo.svg" '
                'alt="CoinAfrique Logo" style="max-width:300px"></div>',
                unsafe_allow_html=True)

with col2:
    selected = st.selectbox("", ["☀️ Light", "🌙 Dark"],
                            index=0 if st.session_state.theme == 'light' else 1,
                            label_visibility="collapsed")
    if selected == "☀️ Light" and st.session_state.theme != 'light':
        st.session_state.theme = 'light'
        st.rerun()
    elif selected == "🌙 Dark" and st.session_state.theme != 'dark':
        st.session_state.theme = 'dark'
        st.rerun()

st.markdown("---")

# SIDEBAR NAVIGATION
# this is the most important part of our project here we get all the navigation we want 

st.sidebar.title("Navigation")

if 'page' not in st.session_state:
    st.session_state.page = "🔍 Scrape Data"
# this are the buttons that are in on the navigation which only require a click only then everything pops up 
nav_opts = ["🔍 Scrape Data", "📤 Upload Data", "📊 Dashboard", "📥 Download Data", "📝 Feedback", "📈 Feedback Analysis"]

for nav in nav_opts:
    if st.sidebar.button(f"**{nav}**", key=f"nav_{nav}", use_container_width=True):
        st.session_state.page = nav

page = st.session_state.page
# Before put thing the main part for scraping we have three links here which carries the images for villa, terrain and appartment
#this helps someone to be sure which exactly what he needs to click
IMGS = {
    'villa': 'https://images.coinafrique.com/thumb_5629986_uploaded_image1_1763558696.jpg',
    'terrain': 'https://images.coinafrique.com/thumb_5654697_uploaded_image1_1764799621.jpg',
    'appartement': 'https://images.coinafrique.com/thumb_5660589_uploaded_image1_1765129781.jpg'
}


# SCRAPE DATA PAGE
# this section helps us do the scraping now 
# this only works after clicking scrape data from the sidebar navigation


if page == "🔍 Scrape Data":
    st.header("🔍 Scrape Real Estate Data")
    st.markdown("---")

    st.markdown("<div style='text-align:center;margin-bottom:30px'>"
                "<h3 style='color:#FF6934'>Select property type and number of pages to scrape</h3>"
                "</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<div class='category-card'><h2>🏘️ Villas</h2><p>Luxury villas and houses</p></div>", unsafe_allow_html=True)
        st.markdown(f"<img src='{IMGS['villa']}' class='property-image'>", unsafe_allow_html=True)
        # here we need to put the number of pages we need to scrape  of which the maximum is 120 
        pages = st.number_input("How many pages to scrape? (Max: 120)", 1, 120, 5, key="villas")
        st.caption(f"You selected {pages} page(s)")
        # this part tells if the scraping is complete by showing a complete blue progress line 
        if st.button("🚀 Scrape Villas", key="btn_villas", use_container_width=True):
            with st.spinner(f"Scraping {pages} pages..."):
                prog = st.progress(0)
                df = scrape_villas(pages, prog)
                if not df.empty:
                    save_to_db(df, 'villas')
                    st.success(f"✅ Successfully scraped {len(df)} villas!")
                    with st.expander("📋 Preview Data"):
                        st.dataframe(df.head(10))
        #after scraping before moving to dashboard we need to clean the scraped data 
        # this enable us to have clean data to run simple analysis in the dashboard
        if st.button("🧹 Clean Villas Data", key="clean_villas", use_container_width=True):
            df_raw = load_from_db('villas')
            if not df_raw.empty:
                df_clean = clean_villas_data(df_raw)
                df_clean = df_clean.drop(columns=['id'], errors='ignore')
                save_to_db(df_clean, 'villas_cleaned')
                st.success(f"✅ Cleaned {len(df_clean)} records!")
                #After cleaning data we now show only the first five rows which in this case we use head and also the last five rows using tail
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write("**First 5 rows:**")
                    st.dataframe(df_clean.head())
                with col_b:
                    st.write("**Last 5 rows:**")
                    st.dataframe(df_clean.tail())
    #we repeat the above process for the second columns where we have terrains
    with col2:
        st.markdown("<div class='category-card'><h2>🏞️ Terrains</h2><p>Land plots and lots</p></div>", unsafe_allow_html=True)
        st.markdown(f"<img src='{IMGS['terrain']}' class='property-image'>", unsafe_allow_html=True)

        pages = st.number_input("How many pages to scrape? (Max: 120)", 1, 120, 5, key="terrains")
        st.caption(f"You selected {pages} page(s)")

        if st.button("🚀 Scrape Terrains", key="btn_terrains", use_container_width=True):
            with st.spinner(f"Scraping {pages} pages..."):
                prog = st.progress(0)
                df = scrape_terrains(pages, prog)
                if not df.empty:
                    save_to_db(df, 'terrains')
                    st.success(f"✅ Successfully scraped {len(df)} terrains!")
                    with st.expander("📋 Preview Data"):
                        st.dataframe(df.head(10))

        if st.button("🧹 Clean Terrains Data", key="clean_terrains", use_container_width=True):
            df_raw = load_from_db('terrains')
            if not df_raw.empty:
                df_clean = clean_terrains_data(df_raw)
                df_clean = df_clean.drop(columns=['id'], errors='ignore')
                save_to_db(df_clean, 'terrains_cleaned')
                st.success(f"✅ Cleaned {len(df_clean)} records!")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write("**First 5 rows:**")
                    st.dataframe(df_clean.head())
                with col_b:
                    st.write("**Last 5 rows:**")
                    st.dataframe(df_clean.tail())
    #we redo the same above process here where we have the appartment scraper 
    with col3:
        st.markdown("<div class='category-card'><h2>🏢 Appartements</h2><p>Apartments and flats</p></div>", unsafe_allow_html=True)
        st.markdown(f"<img src='{IMGS['appartement']}' class='property-image'>", unsafe_allow_html=True)

        pages = st.number_input("How many pages to scrape? (Max: 120)", 1, 120, 5, key="appartements")
        st.caption(f"You selected {pages} page(s)")

        if st.button("🚀 Scrape Appartements", key="btn_appartements", use_container_width=True):
            with st.spinner(f"Scraping {pages} pages..."):
                prog = st.progress(0)
                df = scrape_appartements(pages, prog)
                if not df.empty:
                    save_to_db(df, 'appartements')
                    st.success(f"✅ Successfully scraped {len(df)} apartments!")
                    with st.expander("📋 Preview Data"):
                        st.dataframe(df.head(10))

        if st.button("🧹 Clean Appartements Data", key="clean_appartements", use_container_width=True):
            df_raw = load_from_db('appartements')
            if not df_raw.empty:
                df_clean = clean_appartements_data(df_raw)
                df_clean = df_clean.drop(columns=['id'], errors='ignore')
                save_to_db(df_clean, 'appartements_cleaned')
                st.success(f"✅ Cleaned {len(df_clean)} records!")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write("**First 5 rows:**")
                    st.dataframe(df_clean.head())
                with col_b:
                    st.write("**Last 5 rows:**")
                    st.dataframe(df_clean.tail())


# UPLOAD DATA PAGE
#apart from scrapping data from the the website we have data which we use different scraping method such as web scraper
# we can use this upload button on the navigation part to bring it on board in this case these data is not clean 

elif page == "📤 Upload Data":
    st.header("📤 Upload Data")
    st.markdown("---")
    # and since data comes in different way fro example in this case we have data for villas which is not quite same as terrains data
    # so we have option for each type of data to upload that is villas, terrains, and appartment
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🏘️ Villas")
        f = st.file_uploader("Upload CSV file", type=['csv'], key="up_villas")
        if f:
            df = pd.read_csv(f)
            st.write(f"📊 {len(df)} records found")
            st.dataframe(df.head())
            if st.button("💾 Save to Database", key="save_villas"):
                save_to_db(df, 'villas')
                st.success("✅ Data saved successfully!")

    with col2:
        st.subheader("🏞️ Terrains")
        f = st.file_uploader("Upload CSV file", type=['csv'], key="up_terrains")
        if f:
            df = pd.read_csv(f)
            st.write(f"📊 {len(df)} records found")
            st.dataframe(df.head())
            if st.button("💾 Save to Database", key="save_terrains"):
                save_to_db(df, 'terrains')
                st.success("✅ Data saved successfully!")

    with col3:
        st.subheader("🏢 Appartements")
        f = st.file_uploader("Upload CSV file", type=['csv'], key="up_appartements")
        if f:
            df = pd.read_csv(f)
            st.write(f"📊 {len(df)} records found")
            st.dataframe(df.head())
            if st.button("💾 Save to Database", key="save_appartements"):
                save_to_db(df, 'appartements')
                st.success("✅ Data saved successfully!")

# DASHBOARD PAGE
#after getting data either by scraping which is clean or web scraper or other tools used to scrape data
#we now come here at the dashboard to run som simple analysis to understand our data set before even running more other analysis

elif page == "📊 Dashboard":
    st.header("📊 Analytics Dashboard")
    st.markdown("---")
    # here we get different analytics so for easy visibility 
    dv = load_from_db('villas_cleaned')
    dt = load_from_db('terrains_cleaned')
    da = load_from_db('appartements_cleaned')

    # Summary Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏘️ Total Villas", len(dv))
    with col2:
        st.metric("🏞️ Total Terrains", len(dt))
    with col3:
        st.metric("🏢 Total Appartements", len(da))
    with col4:
        total = len(dv) + len(dt) + len(da)
        st.metric("📊 Total Properties", total)

    st.markdown("---")

    # Villas Analysis
    if not dv.empty:
        st.subheader("🏘️ Villas Analysis")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Price", f"{dv['price'].mean():,.0f} CFA")
        with col2:
            st.metric("Median Price", f"{dv['price'].median():,.0f} CFA")
        with col3:
            st.metric("Avg Rooms", f"{dv['number_of_rooms'].mean():.1f}")

        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.histogram(dv, x='price', nbins=30, title='Villa Price Distribution',
                             labels={'price': 'Price (CFA)', 'count': 'Number of Villas'})
            fig.update_traces(marker_color='#FF6934')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.box(dv, y='price', title='Villa Price Box Plot',
                        labels={'price': 'Price (CFA)'})
            fig.update_traces(marker_color='#FF6934')
            st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        
        with col1:
            rooms_dist = dv['number_of_rooms'].value_counts().sort_index()
            fig = px.bar(x=rooms_dist.index, y=rooms_dist.values, 
                        title='Distribution by Number of Rooms',
                        labels={'x': 'Number of Rooms', 'y': 'Count'})
            fig.update_traces(marker_color='#FF6934')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            top_locations = dv['address'].value_counts().head(10)
            fig = px.bar(x=top_locations.values, y=top_locations.index,
                        orientation='h', title='Top 10 Locations',
                        labels={'x': 'Number of Villas', 'y': 'Location'})
            fig.update_traces(marker_color='#FF6934')
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Terrains Analysis
    if not dt.empty:
        st.subheader("🏞️ Terrains Analysis")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Price", f"{dt['price'].mean():,.0f} CFA")
        with col2:
            st.metric("Median Price", f"{dt['price'].median():,.0f} CFA")
        with col3:
            st.metric("Avg Surface", f"{dt['surface'].mean():.1f} m²")

        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.histogram(dt, x='price', nbins=30, title='Terrain Price Distribution',
                             labels={'price': 'Price (CFA)', 'count': 'Number of Terrains'})
            fig.update_traces(marker_color='#FF4500')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.scatter(dt, x='surface', y='price', title='Price vs Surface Area',
                           labels={'surface': 'Surface (m²)', 'price': 'Price (CFA)'})
            fig.update_traces(marker_color='#FF4500')
            st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.box(dt, y='surface', title='Surface Area Distribution',
                        labels={'surface': 'Surface (m²)'})
            fig.update_traces(marker_color='#FF4500')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            top_locations = dt['address'].value_counts().head(10)
            fig = px.bar(x=top_locations.values, y=top_locations.index,
                        orientation='h', title='Top 10 Locations',
                        labels={'x': 'Number of Terrains', 'y': 'Location'})
            fig.update_traces(marker_color='#FF4500')
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Appartements Analysis
    if not da.empty:
        st.subheader("🏢 Appartements Analysis")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Price", f"{da['price'].mean():,.0f} CFA")
        with col2:
            st.metric("Median Price", f"{da['price'].median():,.0f} CFA")
        with col3:
            st.metric("Avg Rooms", f"{da['number_of_rooms'].mean():.1f}")

        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.histogram(da, x='price', nbins=30, title='Apartment Price Distribution',
                             labels={'price': 'Price (CFA)', 'count': 'Number of Apartments'})
            fig.update_traces(marker_color='#FF8C00')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.box(da, y='price', title='Apartment Price Box Plot',
                        labels={'price': 'Price (CFA)'})
            fig.update_traces(marker_color='#FF8C00')
            st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        
        with col1:
            rooms_dist = da['number_of_rooms'].value_counts().sort_index()
            fig = px.bar(x=rooms_dist.index, y=rooms_dist.values,
                        title='Distribution by Number of Rooms',
                        labels={'x': 'Number of Rooms', 'y': 'Count'})
            fig.update_traces(marker_color='#FF8C00')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            top_locations = da['address'].value_counts().head(10)
            fig = px.bar(x=top_locations.values, y=top_locations.index,
                        orientation='h', title='Top 10 Locations',
                        labels={'x': 'Number of Apartments', 'y': 'Location'})
            fig.update_traces(marker_color='#FF8C00')
            st.plotly_chart(fig, use_container_width=True)

    # Comparative Analysis
    if not dv.empty and not dt.empty and not da.empty:
        st.markdown("---")
        st.subheader("📈 Comparative Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            comparison_data = pd.DataFrame({
                'Property Type': ['Villas', 'Terrains', 'Apartments'],
                'Average Price': [dv['price'].mean(), dt['price'].mean(), da['price'].mean()],
                'Count': [len(dv), len(dt), len(da)]
            })
            
            fig = px.bar(comparison_data, x='Property Type', y='Average Price',
                        title='Average Price by Property Type',
                        labels={'Average Price': 'Price (CFA)'},
                        color='Property Type',
                        color_discrete_sequence=['#FF6934', '#FF4500', '#FF8C00'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.pie(comparison_data, values='Count', names='Property Type',
                        title='Property Distribution',
                        color_discrete_sequence=['#FF6934', '#FF4500', '#FF8C00'])
            st.plotly_chart(fig, use_container_width=True)


# DOWNLOAD DATA PAGE
#since we have cleaned data and already seen the simple analysis 
# we can now download our data in csv form because it is widely used and it is easy to convert to other form like JSON or excel

elif page == "📥 Download Data":
    st.header("📥 Download Data")
    st.markdown("---")

    dv = load_from_db('villas')
    dt = load_from_db('terrains')
    da = load_from_db('appartements')

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🏘️ Villas")
        st.write(f"📊 {len(dv)} records available")
        if not dv.empty:
            csv = dv.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download CSV", csv, "villas.csv", "text/csv", use_container_width=True)

    with col2:
        st.subheader("🏞️ Terrains")
        st.write(f"📊 {len(dt)} records available")
        if not dt.empty:
            csv = dt.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download CSV", csv, "terrains.csv", "text/csv", use_container_width=True)

    with col3:
        st.subheader("🏢 Appartements")
        st.write(f"📊 {len(da)} records available")
        if not da.empty:
            csv = da.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download CSV", csv, "appartements.csv", "text/csv", use_container_width=True)


# FEEDBACK PAGES
# this is important part because now we can get feedback from the user to ensure that the web application was of great use


elif page == "📝 Feedback":
    st.header("📝 Feedback")
    st.markdown("---")
    # here we use kobotoolbox and google form because they are easy to use and also allow collection of data offline especially kobotoolbox
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 KoboToolbox")
        st.markdown('<a href="https://ee.kobotoolbox.org/x/J5vUwPLH" target="_blank">'
                    '<button style="background:#FF6934;color:white;padding:15px 30px;'
                    'border:none;border-radius:10px;font-size:18px;cursor:pointer">Open Survey</button></a>',
                    unsafe_allow_html=True)

    with col2:
        st.subheader("📝 Google Form")
        st.markdown('<a href="https://docs.google.com/forms/d/e/1FAIpQLSd8YW_RsYZA2jJBOQqqZ9TY8usWdsD0_R1SzthnjfkKA1ofiA/viewform" target="_blank">'
                    '<button style="background:#FF6934;color:white;padding:15px 30px;'
                    'border:none;border-radius:10px;font-size:18px;cursor:pointer">Open Form</button></a>',
                    unsafe_allow_html=True)

elif page == "📈 Feedback Analysis":
    st.header("📈 Feedback Analysis")
    st.markdown("---")
    st.info("📊 Feedback analysis will be displayed here once data is collected")


# FOOTER
# this part shows the developer of the application 
# and also to whom the data belong in this case it is CoinAfrique located in senegal

st.markdown("---")
st.markdown("<div style='text-align:center;padding:20px'>"
            "<p style='color:#FF6934;font-weight:600'>Developed by @Joehat | CoinAfrique Senegal</p>"
            "</div>", unsafe_allow_html=True)


#these part enable us to have a decorative page that makes someone enjoy while scraping data online
# this is because scraping data from 120 pages is not a joke it takes alot of time
#Having an interactive web application becomes handy here.
def apply_theme():
    if st.session_state.theme == 'dark':
        st.markdown("""<style>
        .main{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);color:#FAFAFA;min-height:100vh}
        .stButton>button{
            background:linear-gradient(135deg,#FF6934 0%,#FF4500 100%);
            color:white;font-weight:600;border-radius:10px;padding:18px;
            border:none;font-size:16px;width:100%;
            box-shadow:0 4px 12px rgba(255,105,52,0.3);
            transition:all 0.3s ease
        }
        .stButton>button:hover{
            transform:translateY(-2px);
            box-shadow:0 6px 20px rgba(255,105,52,0.5)
        }
        .category-card{
            background:linear-gradient(135deg,#2D3561 0%,#1F2544 100%);
            padding:25px;border-radius:12px;text-align:center;
            color:#FAFAFA;box-shadow:0 8px 20px rgba(0,0,0,0.4);
            margin:10px 0;border:2px solid #FF6934
        }
        .property-image{
            width:100%;height:200px;object-fit:cover;
            border-radius:8px;margin-bottom:15px;
            border:2px solid #FF6934;box-shadow:0 4px 10px rgba(255,105,52,0.3)
        }
        section[data-testid="stSidebar"]{background:linear-gradient(180deg,#1F2544 0%,#16213e 100%)}
        .stMetric{background:linear-gradient(135deg,#2D3561 0%,#1F2544 100%);padding:20px;border-radius:12px;border:2px solid #FF6934;box-shadow:0 4px 15px rgba(255,105,52,0.2)}
        .stMetric label{color:#FF6934 !important;font-weight:600 !important}
        .stMetric [data-testid="stMetricValue"]{color:#00D9FF !important;font-size:28px !important}
        </style>""", unsafe_allow_html=True)
    else:
        st.markdown("""<style>
        .main{background:linear-gradient(135deg,#667eea 0%,#764ba2 50%,#f093fb 100%);color:#1A1A1A;min-height:100vh}
        .stButton>button{
            background:linear-gradient(135deg,#FF6934 0%,#FF4500 100%);
            color:white;font-weight:600;border-radius:10px;padding:18px;
            border:none;font-size:16px;width:100%;
            box-shadow:0 4px 12px rgba(255,105,52,0.3);
            transition:all 0.3s ease
        }
        .stButton>button:hover{
            transform:translateY(-2px);
            box-shadow:0 6px 20px rgba(255,105,52,0.5)
        }
        .category-card{
            background:linear-gradient(135deg,#FFFFFF 0%,#F0E6FF 100%);
            padding:25px;border-radius:12px;text-align:center;
            color:#1A1A1A;box-shadow:0 8px 20px rgba(0,0,0,0.15);
            margin:10px 0;border:2px solid #FF6934
        }
        .property-image{
            width:100%;height:200px;object-fit:cover;
            border-radius:8px;margin-bottom:15px;
            border:2px solid #FF6934;box-shadow:0 4px 10px rgba(255,105,52,0.3)
        }
        section[data-testid="stSidebar"]{background:linear-gradient(180deg,#FFFFFF 0%,#F0E6FF 100%)}
        .stMetric{background:linear-gradient(135deg,#FFFFFF 0%,#FFF5F0 100%);padding:20px;border-radius:12px;border:2px solid #FF6934;box-shadow:0 4px 15px rgba(255,105,52,0.2)}
        .stMetric label{color:#FF6934 !important;font-weight:600 !important}
        .stMetric [data-testid="stMetricValue"]{color:#764ba2 !important;font-size:28px !important}
        </style>""", unsafe_allow_html=True)
