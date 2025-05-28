import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import calendar
import folium
from streamlit_folium import st_folium, folium_static
import requests
import json
import geopandas as gpd
from shapely.geometry import shape
import math
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import time
from branca.colormap import linear

# Meerdere accounts
gebruikers = {
    "admin": "OV2025!",
    "q": "q"
}

# Sessietoestand voor inloggen
if 'ingelogd' not in st.session_state:
    st.session_state.ingelogd = False
if 'gebruiker' not in st.session_state:
    st.session_state.gebruiker = ""

# Als ingelogd, toon de tabs en laad data
if st.session_state.ingelogd:
# Sidebar met tabbladen
    tab1, tab2, tab3 = st.tabs(['Afspraken', 'Gemeentes', 'Behandelaren'])

    # Data inladen
    @st.cache_data
    def data():
        afspraken2020 = pd.read_excel('afspraken 2020.xlsx') 
        afspraken2021 = pd.read_excel('afspraken 2021.xlsx') 
        afspraken2022 = pd.read_excel('afspraken 2022.xlsx') 
        afspraken2023 = pd.read_excel('afspraken 2023.xlsx') 
        afspraken2024 = pd.read_excel('afspraken 2024.xlsx') 
        afspraken2025 = pd.read_excel('afspraken 2025.xlsx')
        return afspraken2020, afspraken2021, afspraken2022, afspraken2023, afspraken2024, afspraken2025

    afspraken2020, afspraken2021, afspraken2022, afspraken2023, afspraken2024, afspraken2025 = data()

    @st.cache_data
    def load_data_factuur():
        factuur = pd.read_excel('Factuurregels 2020-2025.xlsx')
        return factuur

    factuur = load_data_factuur()

    #-------------------------------------------------------------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------------------------------------------------------------

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

    with tab1:

        st.title("Afspraken")
        st.write("In dit tabblad krijg je inzicht in het aantal gehouden afspraken, de bestede minuten door behandelaren en het aantal verstuurde facturen per maand. Met de jaarslider kun je de gegevens filteren voor de jaren 2020 tot 2025. Via de legenda kun je specifieke jaren aan- of uitzetten voor gerichte vergelijking.")

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
            title="Aantal gehouden afspraken per maand",
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

        
    #-------------------------------------------------------------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------------------------------------------------------------
    
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

        fig1.update_layout(title="Hoeveelheid verstuurde facturen per maand",
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

    #-------------------------------------------------------------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------------------------------------------------------------

        maandelijkse_totals = []

        # Voor elke dataframe, jaar en duur groeperen
        for year, df in dataframes.items():
            df['datum'] = pd.to_datetime(df['datum'], format='%d-%m-%Y')
            df['maand'] = df['datum'].dt.month
            df['jaar'] = df['datum'].dt.year  

            # Filter op de geselecteerde maanden (gebruik maandnummers)
            filtered_df = df[(df['maand'] >= start_month) & (df['maand'] <= end_month)]

            # Groepeer per jaar en maand en sommeer de duur
            maand_duur = filtered_df.groupby(['jaar', 'maand'])['duur'].sum().reset_index()

            maandelijkse_totals.append(maand_duur)

        # Combineer de maandelijkse totals van alle jaren in één dataframe
        maandelijkse_totals_df = pd.concat(maandelijkse_totals)

        # Plot met Plotly Express
        fig2 = px.line(maandelijkse_totals_df, 
                    x='maand', 
                    y='duur', 
                    color='jaar', 
                    markers=True)

        fig2.update_layout(
            title="Aantal gehouden minuten per maand",
            xaxis=dict(
                tickmode='array', 
                tickvals=list(range(1, 13)), 
                ticktext=maanden,  # Maandnamen tonen in plaats van nummers
            ),
            yaxis_title="Aantal minuten",
            legend_title="Jaar",
            xaxis_showgrid=True,
            yaxis_showgrid=True
        )

        # Streamlit plot
        st.plotly_chart(fig2)

    #-------------------------------------------------------------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------------------------------------------------------------

    with tab2:
        # Zet de titel
        st.title("Gemeentes")
        st.write("In dit tabblad kun je het aantal verstuurde facturen in detail bekijken, verdeeld over regio's en gemeentes. Gebruik de jaarslider en maandselectie om verschillen in de tijd en tussen gebieden te analyseren. De grafiek toont het aantal facturen per gemeente per maand. Via de legenda kun je specifieke regio's aan- of uitzetten voor gerichte vergelijking. De kaart visualiseert het aantal facturen per regio, waarbij een grotere cirkel een hoger bedrag vertegenwoordigt.")

        # Correcte lijst van jaar-maanden
        jaarmaanden = [
            'Januari 2020', 'Februari 2020', 'Maart 2020', 'April 2020', 'Mei 2020', 'Juni 2020', 'Juli 2020', 'Augustus 2020', 'September 2020', 'Oktober 2020', 'November 2020', 'December 2020',
            'Januari 2021', 'Februari 2021', 'Maart 2021', 'April 2021', 'Mei 2021', 'Juni 2021', 'Juli 2021', 'Augustus 2021', 'September 2021', 'Oktober 2021', 'November 2021', 'December 2021',
            'Januari 2022', 'Februari 2022', 'Maart 2022', 'April 2022', 'Mei 2022', 'Juni 2022', 'Juli 2022', 'Augustus 2022', 'September 2022', 'Oktober 2022', 'November 2022', 'December 2022',
            'Januari 2023', 'Februari 2023', 'Maart 2023', 'April 2023', 'Mei 2023', 'Juni 2023', 'Juli 2023', 'Augustus 2023', 'September 2023', 'Oktober 2023', 'November 2023', 'December 2023',
            'Januari 2024', 'Februari 2024', 'Maart 2024', 'April 2024', 'Mei 2024', 'Juni 2024', 'Juli 2024', 'Augustus 2024', 'September 2024', 'Oktober 2024', 'November 2024', 'December 2024',
            'Januari 2025', 'Februari 2025', 'Maart 2025', 'April 2025', 'Mei 2025', 'Juni 2025', 'Juli 2025', 'Augustus 2025', 'September 2025', 'Oktober 2025', 'November 2025', 'December 2025'
        ]

        # Slider voor het selecteren van maanden
        start_month_name, end_month_name = st.select_slider(
            "Selecteer de maanden", 
            options=jaarmaanden, 
            value=(jaarmaanden[0], jaarmaanden[71]),  # Standaardwaarde is van Januari 2020 tot December 2025
            key="maand_slider2",
            help="Selecteer een periode van maanden van het jaar"
        )

        # Filter de data tussen de geselecteerde indices
        start_index = jaarmaanden.index(start_month_name)
        end_index = jaarmaanden.index(end_month_name)
        gefilterde_maanden = jaarmaanden[start_index:end_index + 1]

        # Regio dictionary (geeft regio's voor verschillende gemeenten)
        dic = {
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
            for regio, gemeenten in dic.items():
                if gemeente in gemeenten:
                    return regio
            return "Onbekend"

        factuur['regio'] = factuur['debiteur'].apply(find_regio)

        # Mapping van Nederlandse maandnamen naar cijfers
        maand_mapping = {
            'Januari': '01', 'Februari': '02', 'Maart': '03', 'April': '04', 'Mei': '05', 'Juni': '06',
            'Juli': '07', 'Augustus': '08', 'September': '09', 'Oktober': '10', 'November': '11', 'December': '12'
        }

        # Converteer geselecteerde maanden naar 'YYYY-MM'
        start_maand = f"{start_month_name.split()[1]}-{maand_mapping[start_month_name.split()[0]]}"
        end_maand = f"{end_month_name.split()[1]}-{maand_mapping[end_month_name.split()[0]]}"

        # Filter de data correct
        factuur_filtered = factuur[
            (factuur['maand'] >= start_maand) &
            (factuur['maand'] <= end_maand)
        ]

        # Groepeer per regio en per maand en sommeer de bedragen
        df_grouped = factuur_filtered.groupby(['maand', 'regio'], as_index=False)['toegewezen_bedrag'].sum()

        # Maak de interactieve grafiek
        fig = px.line(df_grouped, 
                    x='maand', 
                    y='toegewezen_bedrag', 
                    color='regio', 
                    markers=True,
                    title="Hoeveelheid verstuurde facturen per maand per gemeente",
                    labels={'maand': 'Maand', 'toegewezen_bedrag': 'Toegewezen Bedrag (€)', 'regio': 'Regio'})

        # Toon de grafiek in Streamlit
        st.plotly_chart(fig)


    #-------------------------------------------------------------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------------------------------------------------------------

        kleur_mapping = {
            'Alkmaar': 'blue',
            'Bergen (NH.)': 'blue',
            'Castricum': 'blue',
            'Dijk en Waard': 'blue',
            'Heiloo': 'blue',
            'Uitgeest': 'blue',
            'Den Helder': 'green',
            'Schagen': 'green',
            'Texel': 'green',
            'Hollands Kroon': 'green',
            'Beverwijk': 'red',
            'Heemskerk': 'red',
            'Velsen': 'red',
            'Drechterland': 'purple',
            'Enkhuizen': 'purple',
            'Hoorn': 'purple',
            'Koggenland': 'purple',
            'Medemblik': 'purple',
            'Opmeer': 'purple',
            'Stede Broec': 'purple',
            'Bloemendaal': 'orange',
            'Haarlem': 'orange',
            'Heemstede': 'orange',
            'Zandvoort': 'orange',
            'Edam-Volendam': 'brown',
            'Landsmeer': 'brown',
            'Oostzaan': 'brown',
            'Purmerend': 'brown',
            'Waterland': 'brown',
            'Wormerland': 'brown',
            'Zaanstad': 'brown',
            'Langedijk': 'brown',
            'Beemster': 'brown',
            'Heerhugowaard': 'brown',
            'Amsterdam': 'pink'
        }

        st.write("### **Hoeveelheid verstuurde facturen per maand per regio**")
        keuze = st.radio("Kies visualisatie:", ["Kaart met cirkels", "Kaart met gebieden"])

        if keuze == "Kaart met cirkels":
            # Laad GeoJSON
            with open("gemeente_coords.geojson", "r") as f:
                gemeente_data = json.load(f)

            jaar = st.slider("Selecteer jaar", 2020, 2025, 2025)
            factuur_jaar = factuur[factuur['jaar'] == jaar]
            gemeente_bedragen = factuur_jaar.groupby('debiteur')['toegewezen_bedrag'].sum().to_dict()

            features = []
            for feature in gemeente_data['features']:
                gemeente = feature['properties']['name']
                geometry = shape(feature['geometry'])
                kleur = kleur_mapping.get(gemeente, 'gray')
                bedrag = gemeente_bedragen.get(gemeente, 0)
                schaal = 10
                radius = math.sqrt(bedrag) * schaal if bedrag > 0 else 0

                features.append({
                    'geometry': geometry,
                    'name': gemeente,
                    'color': kleur,
                    'radius': radius
                })

            gdf = gpd.GeoDataFrame(features)
            gdf.set_crs("EPSG:4326", allow_override=True, inplace=True)

            def create_map():
                m = folium.Map(location=[52.7, 4.85], zoom_start=9)
                for _, row in gdf.iterrows():
                    lat, lon = row['geometry'].centroid.y, row['geometry'].centroid.x
                    if row['radius'] > 0:
                        folium.Circle(
                            location=[lat, lon],
                            radius=row['radius'],
                            color=row['color'],
                            fill=True,
                            fill_color=row['color'],
                            fill_opacity=0.5,
                            popup=f"{row['name']}: €{gemeente_bedragen.get(row['name'], 0):,.2f}"
                        ).add_to(m)
                return m

            m = create_map()
            st_folium(m, width=700, height=500)

            # Legenda
            st.markdown("""
            <div style='font-size:14px'>
            <div style='display:inline-block; width:10px; height:10px; background:blue; border-radius:50%; margin-right:5px;'></div> Regio Alkmaar
            <div style='display:inline-block; width:10px; height:10px; background:green; border-radius:50%; margin-right:5px; margin-left:20px;'></div> Kop van Noord-Holland<br>
            <div style='display:inline-block; width:10px; height:10px; background:red; border-radius:50%; margin-right:5px;'></div> Regio IJmond
            <div style='display:inline-block; width:10px; height:10px; background:purple; border-radius:50%; margin-right:5px; margin-left:20px;'></div> West-Friesland<br>
            <div style='display:inline-block; width:10px; height:10px; background:orange; border-radius:50%; margin-right:5px;'></div> Zuid Kennermerland
            <div style='display:inline-block; width:10px; height:10px; background:brown; border-radius:50%; margin-right:5px; margin-left:20px;'></div> Zaanstreek-Waterland<br>
            <div style='display:inline-block; width:10px; height:10px; background:pink; border-radius:50%; margin-right:5px;'></div> Regio Amsterdam-Amstelland
            </div>
            """, unsafe_allow_html=True)

        elif keuze == "Kaart met gebieden":
            jaar = st.slider("Selecteer jaar", 2020, 2025, 2025)

            # Filter factuur op gekozen jaar
            factuur_jaar = factuur[factuur['jaar'] == jaar]

            drukte_per_land = factuur_jaar.groupby('debiteur')['toegewezen_bedrag'].sum().to_dict()

            # Ophalen van de GeoJSON
            url = 'https://cartomap.github.io/nl/wgs84/gemeente_2025.geojson'
            response = requests.get(url)
            geojson_data = response.json()

            # Filter de features op basis van 'statnaam' die voorkomen in drukte_per_land
            filtered_features = [
                feature for feature in geojson_data['features']
                if feature['properties']['statnaam'] in drukte_per_land
            ]

            # Normaliseer de drukte voor kleurgebruik
            max_value = max(drukte_per_land.values()) if drukte_per_land else 1
            colormap = linear.Reds_09.scale(0, max_value)

            # Style functie voor kleuren op basis van toegewezen bedrag
            def style_function(feature):
                gemeente = feature['properties']['statnaam']
                waarde = drukte_per_land.get(gemeente, 0)
                return {
                    'fillColor': colormap(waarde),
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.7,
                }

            # Maak de kaart
            m = folium.Map(location=[52.75, 4.7410], zoom_start=9)

            # Voeg elke feature met eigen popup en style toe
            for feature in filtered_features:
                gemeente = feature['properties']['statnaam']
                bedrag = drukte_per_land.get(gemeente, 0)
                bedrag_str = f"€ {bedrag:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                popup_html = f"<strong>{gemeente}</strong><br>Toegewezen bedrag: {bedrag_str}"

                geojson = folium.GeoJson(
                    data=feature,
                    style_function=style_function,
                    tooltip=folium.Tooltip(gemeente),
                    popup=folium.Popup(popup_html, max_width=300)
                )
                geojson.add_to(m)

            # Voeg legenda toe
            colormap.caption = 'Toegewezen bedrag per gemeente'
            colormap.add_to(m)

            folium_static(m, width=700, height=500)

    #-------------------------------------------------------------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------------------------------------------------------------

    with tab3:
        # Dataframes per jaar
        dataframes = {
            2020: afspraken2020,
            2021: afspraken2021,
            2022: afspraken2022,
            2023: afspraken2023,
            2024: afspraken2024,
            2025: afspraken2025
        }

        for jaar in dataframes.keys():
            dataframes[jaar] = dataframes[jaar].merge(
                factuur[['clientcode', 'debiteur']], 
                left_on='clienten_aanwezig', 
                right_on='clientcode', 
                how='left'
            ).rename(columns={'debiteur': 'gemeente'})

        # Streamlit UI
        st.title("Behandelaren")
        st.write("Dit tabblad biedt inzicht in de werkdruk en cliëntenverdeling van behandelaren per regio en gemeente. Gebruik de jaarslider om resultaten over de jaren 2020 tot 2025 te bekijken en selecteer een specifieke regio voor een gerichte analyse. Via de legenda kun je specifieke regio's aan- of uitzetten voor gerichte vergelijking.")

        # Slider voor het jaar
        selected_year = st.slider("Kies een jaar:", min_value=2020, max_value=2025, value=2025)

        df = dataframes[selected_year]

        # Groeperen per uitvoerder en gemeente, en het aantal unieke cliënten tellen
        uitvoerder_counts = df.groupby(['uitvoerder', 'gemeente'])['clienten_aanwezig'].nunique().reset_index()

        dic = {
            'Regio Alkmaar': ['Alkmaar', 'Bergen (NH.)', 'Castricum', 'Dijk en Waard', 'Heiloo', 'Uitgeest'],
            'Kop van Noord-Holland': ['Den Helder', 'Schagen', 'Texel', 'Hollands Kroon'],
            'Regio IJmond': ['Beverwijk', 'Heemskerk', 'Velsen'],
            'West Friesland': ['Drechterland', 'Enkhuizen', 'Hoorn', 'Koggenland', 'Medemblik', 'Opmeer', 'Stede Broec'],
            'Zuid Kennermerland': ['Bloemendaal', 'Haarlem', 'Heemstede', 'Zandvoort'],
            'Regio Zaanstreek Waterland': ['Edam-Volendam', 'Landsmeer', 'Oostzaan', 'Purmerend', 'Waterland', 'Wormerland', 'Zaanstad', 'Langedijk', 'Beemster', 'Heerhugowaard'],
            'Regio Amsterdam-Amstelland': ['Amsterdam']
        }

        # Mapping van gemeente naar regio
        def gemeente_naar_regio(gemeente):
            for regio, gemeentes in dic.items():
                if gemeente in gemeentes:
                    return regio
            return "Onbekend"

        # Nieuwe kolom "regio" toevoegen
        uitvoerder_counts['regio'] = uitvoerder_counts['gemeente'].apply(gemeente_naar_regio)

        # Dropdownmenu voor regioselectie
        regio_keuzes = ["Alle regio's"] + list(dic.keys())
        selected_regio = st.selectbox("Selecteer een regio:", regio_keuzes)

        # Filteren op regio
        if selected_regio != "Alle regio's":
            uitvoerder_counts = uitvoerder_counts[uitvoerder_counts['regio'] == selected_regio]
            kleurvariabele = "gemeente"  # Elke gemeente krijgt een unieke kleur
            hovertemplate = "Aantal unieke cliënten: %{y}<br>Uitvoerder: %{x}"
            customdata = uitvoerder_counts[['gemeente']].values
        else:
            kleurvariabele = "regio"  # Kleur blijft per regio
            uitvoerder_counts = uitvoerder_counts.groupby(["uitvoerder", "regio"])["clienten_aanwezig"].sum().reset_index()
            hovertemplate = "Aantal unieke cliënten: %{y}<br>Uitvoerder: %{x}"
            customdata = uitvoerder_counts[['regio']].values

        # Plot maken met Plotly
        fig3 = px.bar(
            uitvoerder_counts, 
            x='uitvoerder', 
            y='clienten_aanwezig', 
            color=kleurvariabele, 
            title="Aantal cliënten per behandelaar per regio/gemeente", 
            labels={'uitvoerder': 'Uitvoerder', 'clienten_aanwezig': 'Aantal unieke cliënten', kleurvariabele: kleurvariabele.capitalize()}, 
            barmode='stack'  
        )

        # Pas de hoverdata aan
        fig3.update_traces(hovertemplate=hovertemplate, customdata=customdata)

        fig3.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig3)

    #---------------------------------------------------------------------------------------------------------------------------------------------------------------

    #---------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Tellen van het aantal afspraken per uitvoerder en gemeente
        afspraken_per_uitvoerder = df.groupby(['uitvoerder', 'gemeente']).size().reset_index(name='aantal_afspraken')

    # Gemeente omzetten naar regio
        afspraken_per_uitvoerder['regio'] = afspraken_per_uitvoerder['gemeente'].apply(gemeente_naar_regio)

    # Groeperen op uitvoerder, regio en gemeente
        afspraken_per_uitvoerder = afspraken_per_uitvoerder.groupby(['uitvoerder', 'gemeente', 'regio'])['aantal_afspraken'].sum().reset_index()

    # **Filter op geselecteerde regio**
        if selected_regio != "Alle regio's":
            afspraken_per_uitvoerder = afspraken_per_uitvoerder[afspraken_per_uitvoerder['regio'] == selected_regio]
            kleurvariabele = "gemeente"  # Als een regio is geselecteerd, kleur per gemeente
        else:
            kleurvariabele = "regio"  # Als alle regio's worden getoond, kleur per regio

    # Nieuwe plot maken
        fig6 = px.bar(
            afspraken_per_uitvoerder, 
            x='uitvoerder', 
            y='aantal_afspraken', 
            color=kleurvariabele,  # Dynamische kleur
            title="Aantal gehouden afspraken per behandelaar per regio/gemeente", 
            labels={'uitvoerder': 'Uitvoerder', 'aantal_afspraken': 'Aantal afspraken', kleurvariabele: kleurvariabele.capitalize()}, 
            barmode='stack'  # Zorgt ervoor dat de gemeentes/regio's per uitvoerder gestapeld worden
    )

        fig6.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig6)

    #---------------------------------------------------------------------------------------------------------------------------------------------------------------

    #---------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Tellen van de duur per uitvoerder en gemeente (in plaats van aantal afspraken)
        afspraken_per_uitvoerder = df.groupby(['uitvoerder', 'gemeente'])['duur'].sum().reset_index(name='totaal_duur')

    # Gemeente omzetten naar regio
        afspraken_per_uitvoerder['regio'] = afspraken_per_uitvoerder['gemeente'].apply(gemeente_naar_regio)

    # Groeperen op uitvoerder, regio en gemeente
        afspraken_per_uitvoerder = afspraken_per_uitvoerder.groupby(['uitvoerder', 'gemeente', 'regio'])['totaal_duur'].sum().reset_index()

    # **Filter op geselecteerde regio**
        if selected_regio != "Alle regio's":
            afspraken_per_uitvoerder = afspraken_per_uitvoerder[afspraken_per_uitvoerder['regio'] == selected_regio]
            kleurvariabele = "gemeente"  # Als een regio is geselecteerd, kleur per gemeente
        else:
            kleurvariabele = "regio"  # Als alle regio's worden getoond, kleur per regio

    # Nieuwe plot maken
        fig7 = px.bar(
        afspraken_per_uitvoerder, 
        x='uitvoerder', 
        y='totaal_duur',  # Gebruik de som van de duur
        color=kleurvariabele,  # Dynamische kleur
        title="Aantal gehouden minuten per behandelaar per regio/gemeente", 
        labels={'uitvoerder': 'Uitvoerder', 'totaal_duur': 'Aantal minuten', kleurvariabele: kleurvariabele.capitalize()}, 
        barmode='stack'  # Zorgt ervoor dat de gemeentes/regio's per uitvoerder gestapeld worden
    )

        fig7.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig7)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------------------------------------


# Login formulier tonen als nog niet ingelogd
if not st.session_state.ingelogd:
    st.title("Inloggen vereist")
    with st.form("login_form"):
        gebruikersnaam = st.text_input("Gebruikersnaam")
        wachtwoord = st.text_input("Wachtwoord", type="password")
        submitted = st.form_submit_button("Inloggen")
        if submitted:
            if gebruikersnaam in gebruikers and wachtwoord == gebruikers[gebruikersnaam]:
                st.session_state.ingelogd = True
                st.session_state.gebruiker = gebruikersnaam
            else:
                st.error("Gebruikersnaam of wachtwoord is fout")