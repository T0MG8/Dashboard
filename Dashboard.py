import streamlit as st
import pandas as pd
import plotly.express as px
import calendar

# Functie om de afspraken data in te lezen en te verwerken
@st.cache_data
def load_afspraken_data():
    jaren = [2020, 2021, 2022, 2023, 2024]
    bestanden = [f"afspraken {jaar}.xlsx" for jaar in jaren]
    df_lijst = []

    for jaar, bestand in zip(jaren, bestanden):
        df = pd.read_excel(bestand)
        df['datum'] = pd.to_datetime(df['datum'], dayfirst=True)
        df['maand'] = df['datum'].dt.strftime('%B')
        df['jaar'] = jaar  # Jaar toevoegen als aparte kolom
        df_lijst.append(df)

    # Alle data samenvoegen
    return pd.concat(df_lijst)

# Functie om de factuurdata in te lezen en te verwerken
@st.cache_data
def load_factuur_data():
    factuur = pd.read_excel("Factuurregels 2020-2024.xlsx")
    factuur = factuur[['clientcode', 'totaalbedrag', 'toegewezen_bedrag', 'status', 'factuurdatum', 'debiteur']]
    factuur["factuurdatum"] = pd.to_datetime(factuur["factuurdatum"], dayfirst=True)
    factuur = factuur[factuur["status"] == "toegewezen"]
    factuur["jaar"] = factuur["factuurdatum"].dt.year
    factuur["maand"] = factuur["factuurdatum"].dt.month  # Maand als nummer (1-12)
    return factuur

# Functie om de grafiek voor afspraken te genereren
@st.cache_data
def create_afspraken_plot(df_groep_filtered):
    fig = px.line(df_groep_filtered, x='maand', y='aantal', color='jaar', markers=True,
                  title='Aantal Afspraken per Maand per Jaar')

    # Pas hovertemplate aan voor de gefilterde grafiek
    fig.update_traces(
        hovertemplate='<br>Aantal: %{y}<br>'
    )

    # Layout aanpassingen voor de gefilterde grafiek
    fig.update_layout(
        xaxis_title='Maand', 
        yaxis_title='Aantal afspraken', 
        legend_title='Jaar',
        xaxis=dict(showgrid=True),  # Zet de gridlijnen aan voor de x-as
        yaxis=dict(showgrid=True)   # Zet de gridlijnen aan voor de y-as
    )
    return fig

# Functie om de grafiek voor facturen te genereren
@st.cache_data
def create_facturen_plot(factuur_grouped_filtered):
    fig1 = px.line(
        factuur_grouped_filtered, 
        x="maand_naam", 
        y="totaalbedrag", 
        color="jaar", 
        markers=True, 
        title="Toegewezen facturen per maand (2020-2024)",
        labels={"maand_naam": "Maand", "totaalbedrag": "Totaalbedrag (€)", "jaar": "Jaar"},
    )

    fig1.update_traces(
        hovertemplate='<br>Aantal: %{y}<br>'
    )

        # Zet de gridlijnen aan voor zowel de x- als de y-as
    fig1.update_layout(
        xaxis=dict(showgrid=True),  # Zet de gridlijnen aan voor de x-as
        yaxis=dict(showgrid=True)   # Zet de gridlijnen aan voor de y-as
    )

    return fig1


# Sidebar voor navigatie
pagina_keuze = st.sidebar.selectbox("Kies een pagina", ["Aantal Afspraken per Maand", "Andere Pagina"])

# Afspraken data inladen
df_all = load_afspraken_data()

# Aantal afspraken per maand per jaar tellen
df_groep = df_all.groupby(['jaar', 'maand']).size().reset_index(name='aantal')

# Sorteer maanden op kalender volgorde
maand_volgorde = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
df_groep['maand'] = pd.Categorical(df_groep['maand'], categories=maand_volgorde, ordered=True)
df_groep = df_groep.sort_values(['jaar', 'maand'])

# Factuurdata inladen
factuur = load_factuur_data()

# Groepeer en sommeer het totaalbedrag per maand per jaar voor facturen
factuur_grouped = factuur.groupby(["jaar", "maand"])["totaalbedrag"].sum().reset_index()

# Converteer maandnummers naar maandnamen
factuur_grouped["maand_naam"] = factuur_grouped["maand"].apply(lambda x: calendar.month_name[int(x)])

# Zet de maandnummers om naar een gecategoriseerd type voor de juiste sortering
factuur_grouped["maand_naam"] = pd.Categorical(factuur_grouped["maand_naam"], categories=maand_volgorde, ordered=True)

# Groepeer opnieuw en sorteer op maand en jaar
factuur_grouped = factuur_grouped.sort_values(["maand", "jaar"])

# Als de gebruiker 'Aantal Afspraken per Maand' selecteert, voer de bijbehorende code uit
if pagina_keuze == "Aantal Afspraken per Maand":
    st.title("Aantal Afspraken per Maand per Jaar")

    # Slider voor maanden
    geselecteerde_maanden = st.select_slider(
        "Selecteer maanden", 
        options=maand_volgorde,  # Geef de maanden als opties door
        value=(maand_volgorde[0], maand_volgorde[-1]),  # Standaard waarde is van januari tot december
        help="Kies het bereik van maanden om weer te geven."
    )

    # Filter de geselecteerde maanden
    maand_start, maand_einde = maand_volgorde.index(geselecteerde_maanden[0]), maand_volgorde.index(geselecteerde_maanden[1])
    geselecteerde_maanden_namen = maand_volgorde[maand_start:maand_einde + 1]

    # Filter de data voor beide grafieken
    df_groep_filtered = df_groep[df_groep['maand'].isin(geselecteerde_maanden_namen)]
    factuur_grouped_filtered = factuur_grouped[factuur_grouped["maand_naam"].isin(geselecteerde_maanden_namen)]

    # De gefilterde data tonen in de grafiek voor afspraken
    fig = create_afspraken_plot(df_groep_filtered)
    st.plotly_chart(fig)

    # De gefilterde data tonen in de grafiek voor facturen
    fig1 = create_facturen_plot(factuur_grouped_filtered)
    st.plotly_chart(fig1)

# Andere pagina
if pagina_keuze == "Andere Pagina":
    st.title("Andere Pagina")
    st.write("Hier komt de inhoud van de andere pagina.")