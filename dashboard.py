import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import calendar

# Data inladen
@st.cache_data
def load_data_afspraken():
    afspraken2020 = pd.read_excel('afspraken 2020.xlsx') 
    afspraken2021 = pd.read_excel('afspraken 2021.xlsx') 
    afspraken2022 = pd.read_excel('afspraken 2022.xlsx') 
    afspraken2023 = pd.read_excel('afspraken 2023.xlsx') 
    afspraken2024 = pd.read_excel('afspraken 2024.xlsx') 
    return afspraken2020, afspraken2021, afspraken2022, afspraken2023, afspraken2024

afspraken2020, afspraken2021, afspraken2022, afspraken2023, afspraken2024 = load_data_afspraken()

@st.cache_data
def load_data_factuur():
    factuur = pd.read_excel('Factuurregels 2020-2024.xlsx')
    return factuur

factuur = load_data_factuur()

# Maandnamen lijst voor slider
maanden = ['Januari', 'Februari', 'Maart', 'April', 'Mei', 'Juni', 'Juli', 'Augustus', 'September', 'Oktober', 'November', 'December']

# Maak een mapping van maandnummer naar maandnaam
maand_mapping = {i + 1: maanden[i] for i in range(len(maanden))}

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

# Toon de geselecteerde maanden (met maandnamen)
st.write(f"Geselecteerde periode: {start_month_name} tot {end_month_name}")

# Lijst van dataframes en corresponderende jaartallen
dataframes = {
    2020: afspraken2020,
    2021: afspraken2021,
    2022: afspraken2022,
    2023: afspraken2023,
    2024: afspraken2024
}

# Plotly figuur voor afspraken
fig = go.Figure()

# Voor elke dataframe een lijn toevoegen
for year, df in dataframes.items():
    df['datum'] = pd.to_datetime(df['datum'], format='%d-%m-%Y')
    df['maand'] = df['datum'].dt.month

    # Filter op geselecteerde maanden (gebruik maandnummers)
    filtered_df = df[(df['maand'] >= start_month) & (df['maand'] <= end_month)]

    maand_telling = filtered_df['maand'].value_counts().sort_index()

    fig.add_trace(go.Scatter(
        x=maand_telling.index,
        y=maand_telling.values,
        mode='lines+markers',
        name=f'{year}'
    ))

fig.update_traces(hovertemplate='<br>Aantal: %{y}<br>')
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

fig1.update_layout(
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
