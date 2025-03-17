import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

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

# Lijst van dataframes en corresponderende jaartallen
dataframes = {
    2020: afspraken2020,
    2021: afspraken2021,
    2022: afspraken2022,
    2023: afspraken2023,
    2024: afspraken2024
}

# Plotly figuur
fig = go.Figure()

# Voor elke dataframe een lijn toevoegen
for year, df in dataframes.items():
    # Datum kolom omzetten naar datetime-formaat
    df['datum'] = pd.to_datetime(df['datum'], format='%d-%m-%Y')
    
    # Maand extracten
    df['maand'] = df['datum'].dt.month
    
    # Afspraken per maand tellen
    maand_telling = df['maand'].value_counts().sort_index()
    
    # Plot toevoegen
    fig.add_trace(go.Scatter(
        x=maand_telling.index,
        y=maand_telling.values,
        mode='lines+markers',
        name=f'{year}'
    ))  

fig.update_traces(hovertemplate='<br>Aantal: %{y}<br>')

# Layout aanpassen
fig.update_layout(
    title="Aantal afspraken per maand",
    xaxis=dict(title="Maand", tickmode='array', showgrid=True, tickvals=list(range(1, 13)), ticktext=['Jan', 'Feb', 'Mrt', 'Apr', 'Mei', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']),
    yaxis_title="Aantal afspraken",
    legend_title="Jaar",
    yaxis=dict(showgrid=True)
    )

# Streamlit plotten
st.plotly_chart(fig)

# Streamlit titel
st.title("Toegewezen Bedrag per Maand per Jaar")

# Zorg ervoor dat factuurdatum in datetime-formaat is
factuur['factuurdatum'] = pd.to_datetime(factuur['factuurdatum'], dayfirst=True)

# Extraheer jaar en maand
factuur['jaar'] = factuur['factuurdatum'].dt.year
factuur['maand'] = factuur['factuurdatum'].dt.month

# Groepeer per jaar en maand en sommeer het toegewezen bedrag
maandelijkse_totals = factuur.groupby(['jaar', 'maand'])['toegewezen_bedrag'].sum().reset_index()

# Plot met Plotly
fig1 = px.line(maandelijkse_totals, 
              x='maand', 
              y='toegewezen_bedrag', 
              color='jaar',
              markers=True,
              title="Toegewezen Bedrag per Maand per Jaar")

fig1.update_layout(
    xaxis=dict(tickmode='array', tickvals=list(range(1, 13)), 
               ticktext=['Jan', 'Feb', 'Mrt', 'Apr', 'Mei', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']),
    yaxis_title="Totaal Bedrag",
    legend_title="Jaar",
    xaxis_showgrid=True,
    yaxis_showgrid=True
)

# Streamlit plot
st.plotly_chart(fig1)