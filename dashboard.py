import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Sidebar met tabbladen
pagina = st.sidebar.radio("Selecteer een pagina", ['Afspraken', 'Factuur'])

# Data voor afspraken (voorbeeld)
dataframes = {
    2022: pd.DataFrame({'datum': ['01-01-2022', '15-02-2022', '10-03-2022', '20-03-2022', '05-04-2022']}),
    2023: pd.DataFrame({'datum': ['05-01-2023', '12-02-2023', '22-03-2023', '15-04-2023']})
}

# Data voor facturen (voorbeeld)
factuur = pd.DataFrame({
    'factuurdatum': ['01-01-2022', '10-02-2022', '20-03-2022', '15-04-2022', '10-05-2022', '05-01-2023', '12-02-2023'],
    'toegewezen_bedrag': [100, 200, 300, 400, 500, 600, 700]
})

# Tabblad 'Afspraken'
if pagina == 'Afspraken':
    fig = go.Figure()
    for year, df in dataframes.items():
        df['datum'] = pd.to_datetime(df['datum'], format='%d-%m-%Y')
        df['maand'] = df['datum'].dt.month
        maand_telling = df['maand'].value_counts().sort_index()
        fig.add_trace(go.Scatter(
            x=maand_telling.index,
            y=maand_telling.values,
            mode='lines+markers',
            name=f'{year}'
        ))  
    fig.update_traces(hovertemplate='<br>Aantal: %{y}<br>')
    fig.update_layout(
        title="Aantal afspraken per maand",
        xaxis=dict(title="Maand", tickmode='array', tickvals=list(range(1, 13)), 
                   ticktext=['Jan', 'Feb', 'Mrt', 'Apr', 'Mei', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']),
        yaxis_title="Aantal afspraken",
        legend_title="Jaar",
        yaxis=dict(showgrid=True)
    )
    st.plotly_chart(fig)

# Tabblad 'Factuur'
elif pagina == 'Factuur':
    factuur['factuurdatum'] = pd.to_datetime(factuur['factuurdatum'], dayfirst=True)
    factuur['jaar'] = factuur['factuurdatum'].dt.year
    factuur['maand'] = factuur['factuurdatum'].dt.month
    maandelijkse_totals = factuur.groupby(['jaar', 'maand'])['toegewezen_bedrag'].sum().reset_index()
    fig1 = px.line(maandelijkse_totals, 
                   x='maand', 
                   y='toegewezen_bedrag', 
                   color='jaar',
                   markers=True)
    fig1.update_layout(
        xaxis=dict(tickmode='array', tickvals=list(range(1, 13)), 
                   ticktext=['Jan', 'Feb', 'Mrt', 'Apr', 'Mei', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']),
        yaxis_title="Totaal Bedrag",
        legend_title="Jaar",
        xaxis_showgrid=True,
        yaxis_showgrid=True
    )
    st.plotly_chart(fig1)