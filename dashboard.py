import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import calendar
import folium
from streamlit_folium import st_folium
import requests
import json
import geopandas as gpd
from shapely.geometry import shape


# Sidebar met tabbladen
pagina = st.sidebar.radio("Selecteer een pagina", ['Afspraken', 'Gemeentes', 'Behandelaren'])

# Data inladen
@st.cache_data
def load_data_afspraken():
    afspraken2020 = pd.read_excel('afspraken 2020.xlsx') 
    afspraken2021 = pd.read_excel('afspraken 2021.xlsx') 
    afspraken2022 = pd.read_excel('afspraken 2022.xlsx') 
    afspraken2023 = pd.read_excel('afspraken 2023.xlsx') 
    afspraken2024 = pd.read_excel('afspraken 2024.xlsx') 
    afspraken2025 = pd.read_excel('afspraken 2025.xlsx')
    return afspraken2020, afspraken2021, afspraken2022, afspraken2023, afspraken2024, afspraken2025

afspraken2020, afspraken2021, afspraken2022, afspraken2023, afspraken2024, afspraken2025 = load_data_afspraken()

@st.cache_data
def load_data_factuur():
    factuur = pd.read_excel('Factuurregels 2020-2024.xlsx')
    return factuur

factuur = load_data_factuur()

# Maandnamen lijst voor slider
maanden = ['Januari', 'Februari', 'Maart', 'April', 'Mei', 'Juni', 'Juli', 'Augustus', 'September', 'Oktober', 'November', 'December']

# Maak een mapping van maandnummer naar maandnaam
maand_mapping = {i + 1: maanden[i] for i in range(len(maanden))}

# Lijst van dataframes en corresponderende jaartallen
dataframes = {
    2020: afspraken2020,
    2021: afspraken2021,
    2022: afspraken2022,
    2023: afspraken2023,
    2024: afspraken2024,
    2025: afspraken2025
}

if pagina == 'Afspraken':
    # Gebruik select_slider in plaats van slider
    start_month_name, end_month_name = st.select_slider(
        "Selecteer de maanden", 
        options=maanden, 
        value=(maanden[0], maanden[11]), 
        key="maand_slider",
        help="Selecteer een periode van maanden van het jaar"
    )

    # Zet de geselecteerde maandnamen om naar maandnummers
    start_month = maanden.index(start_month_name) + 1  # Maandnaam naar maandnummer
    end_month = maanden.index(end_month_name) + 1      # Maandnaam naar maandnummer

# Plotly figuur voor afspraken
    fig = go.Figure()

# Voor elke dataframe een lijn toevoegen
    for year, df in dataframes.items():
        df['datum'] = pd.to_datetime(df['datum'], format='%d-%m-%Y')
        df['maand'] = df['datum'].dt.month

    # Filter op geselecteerde maanden (gebruik maandnummers)
        filtered_df = df[(df['maand'] >= start_month) & (df['maand'] <= end_month)]
    
    # Bereken totaal aantal afspraken voor dat jaar
        totaal_afspraken = filtered_df.shape[0]

        maand_telling = filtered_df['maand'].value_counts().sort_index()

        fig.add_trace(go.Scatter(
            x=maand_telling.index,
            y=maand_telling.values,
            mode='lines+markers',
            name=f'{year}',
            hovertemplate=f"    Maand: %{{x}}<br>Aantal: %{{y}}<br>Totaal {year}: {totaal_afspraken}"
        ))

    fig.update_layout(
        title="Aantal afspraken per maand",
        xaxis=dict(
            title="Maand", 
            tickmode='array', 
            showgrid=True, 
            tickvals=list(range(1, 13)), 
            ticktext=maanden  # Maandnamen tonen in plaats van nummers
        ),
        yaxis_title="Aantal afspraken",
        legend_title="Jaar",
        yaxis=dict(showgrid=True)
    )

    st.plotly_chart(fig)


    # Zorg ervoor dat factuurdatum in datetime-formaat is
    factuur['factuurdatum'] = pd.to_datetime(factuur['factuurdatum'], dayfirst=True)

    # Extraheer jaar en maand
    factuur['jaar'] = factuur['factuurdatum'].dt.year
    factuur['maand'] = factuur['factuurdatum'].dt.month

    # Filter op de geselecteerde maanden (gebruik maandnummers)
    filtered_factuur = factuur[(factuur['maand'] >= start_month) & (factuur['maand'] <= end_month)]

    # Groepeer per jaar en maand en sommeer het toegewezen bedrag
    maandelijkse_totals = filtered_factuur.groupby(['jaar', 'maand'])['toegewezen_bedrag'].sum().reset_index()

    # Plot met Plotly
    fig1 = px.line(maandelijkse_totals, 
                   x='maand', 
                   y='toegewezen_bedrag', 
                   color='jaar',
                   markers=True)

    fig1.update_layout(title="Totaalbedrag van verstuurde facturen per maand",
        xaxis=dict(
            tickmode='array', 
            tickvals=list(range(1, 13)), 
            ticktext=maanden,  # Maandnamen tonen in plaats van nummers
        ),
        yaxis_title="Totaal Bedrag",
        legend_title="Jaar",
        xaxis_showgrid=True,
        yaxis_showgrid=True
    )

    # Streamlit plot
    st.plotly_chart(fig1)

elif pagina == 'Gemeentes':
# Zet de titel
    st.title("📊 Facturen per gemeente per maand")

# Correcte lijst van jaar-maanden
    jaarmaanden = [
    'Januari 2020', 'Februari 2020', 'Maart 2020', 'April 2020', 'Mei 2020', 'Juni 2020', 'Juli 2020', 'Augustus 2020', 'September 2020', 'Oktober 2020', 'November 2020', 'December 2020',
    'Januari 2021', 'Februari 2021', 'Maart 2021', 'April 2021', 'Mei 2021', 'Juni 2021', 'Juli 2021', 'Augustus 2021', 'September 2021', 'Oktober 2021', 'November 2021', 'December 2021',
    'Januari 2022', 'Februari 2022', 'Maart 2022', 'April 2022', 'Mei 2022', 'Juni 2022', 'Juli 2022', 'Augustus 2022', 'September 2022', 'Oktober 2022', 'November 2022', 'December 2022',
    'Januari 2023', 'Februari 2023', 'Maart 2023', 'April 2023', 'Mei 2023', 'Juni 2023', 'Juli 2023', 'Augustus 2023', 'September 2023', 'Oktober 2023', 'November 2023', 'December 2023',
    'Januari 2024', 'Februari 2024', 'Maart 2024', 'April 2024', 'Mei 2024', 'Juni 2024', 'Juli 2024', 'Augustus 2024', 'September 2024', 'Oktober 2024', 'November 2024', 'December 2024'
]

# Slider voor het selecteren van maanden
    start_month_name, end_month_name = st.select_slider(
        "Selecteer de maanden", 
        options=jaarmaanden, 
        value=(jaarmaanden[0], jaarmaanden[59]),  # Standaardwaarde is van Januari 2020 tot December 2020
        key="maand_slider",
        help="Selecteer een periode van maanden van het jaar"
)

# Zet de geselecteerde maandnamen om naar maandnummers
    start_month = jaarmaanden.index(start_month_name) + 1  # Maandnaam naar maandnummer (1-based)
    end_month = jaarmaanden.index(end_month_name) + 1      # Maandnaam naar maandnummer (1-based)

# Regio dictionary (geeft regio's voor verschillende gemeenten)
    dict = {
    'Regio Alkmaar': ['Alkmaar', 'Bergen (NH.)', 'Castricum', 'Dijk en Waard', 'Heiloo', 'Uitgeest'],
    'Kop van Noord-Holland': ['Den Helder', 'Schagen', 'Texel', 'Hollands Kroon'],
    'Regio IJmond': ['Beverwijk', 'Heemskerk', 'Velsen'],
    'West Friesland': ['Drechterland', 'Enkhuizen', 'Hoorn', 'Koggenland', 'Medemblik', 'Opmeer', 'Stede Broec'],
    'Zuid Kennermerland': ['Bloemendaal', 'Haarlem', 'Heemstede', 'Zandvoort'],
    'Regio Zaanstreek Waterland': ['Edam-Volendam', 'Landsmeer', 'Oostzaan', 'Purmerend', 'Waterland', 'Wormerland', 'Zaanstad', 'Langedijk', 'Beemster', 'Heerhugowaard'],
    'Regio Amsterdam-Amstelland': ['Amsterdam']
}

# Converteer factuurdatum naar datetime en extraheer de maand als 'YYYY-MM'
    factuur['factuurdatum'] = pd.to_datetime(factuur['factuurdatum'], dayfirst=True)
    factuur['maand'] = factuur['factuurdatum'].dt.strftime('%Y-%m')

# Voeg de regio toe aan het DataFrame
    def find_regio(gemeente):
        for regio, gemeenten in dict.items():
            if gemeente in gemeenten:
                return regio
        return "Onbekend"

    factuur['regio'] = factuur['debiteur'].apply(find_regio)

# Filter de data op basis van de geselecteerde maanden
    factuur_filtered = factuur[
        (factuur['maand'] >= start_month_name.split()[1] + '-' + start_month_name.split()[0][:3]) & 
        (factuur['maand'] <= end_month_name.split()[1] + '-' + end_month_name.split()[0][:3])
]

# Groepeer per regio en per maand en sommeer de bedragen
    df_grouped = factuur_filtered.groupby(['maand', 'regio'], as_index=False)['toegewezen_bedrag'].sum()

# Maak de interactieve grafiek
    fig = px.line(df_grouped, 
                  x='maand', 
                  y='toegewezen_bedrag', 
                  color='regio', 
                markers=True,
                title="Facturen per regio per maand",
                labels={'maand': 'Maand', 'toegewezen_bedrag': 'Toegewezen Bedrag (€)', 'regio': 'Regio'})

# Toon de grafiek in Streamlit
    st.plotly_chart(fig)


# Groepeer per regio en per maand en tel de rijen
    df_grouped = factuur_filtered.groupby(['maand', 'regio'], as_index=False).size()

# Hernoem de kolom 'size' naar een meer betekenisvolle naam, bijvoorbeeld 'Aantal Facturen'
    df_grouped.rename(columns={'size': 'Aantal Facturen'}, inplace=True)

# Maak de interactieve grafiek
    fig5 = px.line(df_grouped, 
                  x='maand', 
                  y='Aantal Facturen', 
                  color='regio', 
                markers=True,
                title="Aantal afspraken per regio per maand",
                labels={'maand': 'Maand', 'Aantal Facturen': 'Aantal Facturen', 'regio': 'Regio'})
    
    

# Toon de grafiek in Streamlit
    st.plotly_chart(fig5)







# Laad het GeoJSON bestand
    file_path = 'gemeente_coords.geojson'

    with open(file_path, 'r') as f:
        gemeente_data = json.load(f)

# Maak een lijst van geometrieën en properties
    features = []
    for feature in gemeente_data['features']:
        gemeente = feature['properties']['name']
        coords = feature['geometry']['coordinates']
    
    # Zet de geometrie om naar een shapely object
        geometry = shape(feature['geometry'])  # Gebruik shapely.geometry om de geometrie om te zetten
    
    # Voeg geometrie en properties toe als een dict
        features.append({
            'geometry': geometry,
            'name': gemeente  # We slaan de naam op als 'name' in plaats van 'properties'
    })

# Maak een GeoDataFrame van de features
    gdf = gpd.GeoDataFrame(features)

# Controleer de kolommen van de GeoDataFrame
    print(gdf.columns)

# Stel het CRS in op EPSG:4326
    gdf.set_crs("EPSG:4326", allow_override=True, inplace=True)

# Functie om de kaart te maken
    def create_map():
    # Maak een kaart van Noord-Holland
        m = folium.Map(location=[52.65, 4.85], zoom_start=9)

    # Voeg cirkels toe voor elke gemeente zonder markers
        for _, row in gdf.iterrows():
            print(row)  # Debug: Print de volledige row om te inspecteren
            gemeente = row['name']  # Haal de naam uit de kolom 'name' (geen 'properties' meer)
            lat = row['geometry'].centroid.y  # Haal de latitude (y) uit de geometrie
            lon = row['geometry'].centroid.x  # Haal de longitude (x) uit de geometrie

        # Voeg een cirkel toe voor elke gemeente
            folium.Circle(
                location=[lat, lon], 
                radius=3000, # Straal in meters (bijv. 5 km)
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=0.5,
                popup=gemeente
            ).add_to(m)

        return m

# Streamlit titel en kaart
    st.title("Kaart van Noord-Holland")
    m = create_map()  # De kaart aanmaken
    st_folium(m, width=700, height=500)







elif pagina == 'Behandelaren':
    st.title("Overzicht van Behandelaren")
    st.write("Hier komt informatie over behandelaren.")

