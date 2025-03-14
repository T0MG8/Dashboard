import streamlit as st
import pandas as pd
import plotly.express as px

# Streamlit titel
st.title("Aantal afspraken per maand per jaar")

# afspraken2020 = pd.read_excel('afspraken 2020.xlsx')
afspraken2021 = pd.read_excel('Data/afspraken 2021.xlsx')
afspraken2022 = pd.read_excel('Data/afspraken 2022.xlsx')
afspraken2023 = pd.read_excel('Data/afspraken 2023.xlsx')
afspraken2024 = pd.read_excel('Data/afspraken 2024.xlsx')
afspraken = pd.concat([afspraken2021, afspraken2022, afspraken2023, afspraken2024], ignore_index=True)

factuur = pd.read_excel('./data/factuurregels_2020-2024.xlsx')
factuur = factuur[['clientcode', 'totaalbedrag', 'toegewezen_bedrag', 'status', 'factuurdatum', 'debiteur']]
factuur["factuurdatum"] = pd.to_datetime(factuur["factuurdatum"], dayfirst=True)
factuur = factuur[factuur["status"] == "toegewezen"]
factuur["jaar"] = factuur["factuurdatum"].dt.year
factuur["maand"] = factuur["factuurdatum"].dt.month



# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import calendar

# afspraken2020 = pd.read_excel('./data/afspraken 2020.xlsx') 
# afspraken2021 = pd.read_excel('./data/afspraken 2021.xlsx')
# afspraken2022 = pd.read_excel('./data/afspraken 2022.xlsx')
# afspraken2023 = pd.read_excel('./data/afspraken 2023.xlsx')
# afspraken2024 = pd.read_excel('./data/afspraken 2024.xlsx')

# # Samenvoegen van alle data
# afspraken_all = pd.concat([afspraken2020, afspraken2021, afspraken2022, afspraken2023, afspraken2024], ignore_index=True)

# factuur = pd.read_excel('./data/factuurregels_2020-2024.xlsx')
# factuur = factuur[['clientcode', 'totaalbedrag', 'toegewezen_bedrag', 'status', 'factuurdatum', 'debiteur']]
# factuur["factuurdatum"] = pd.to_datetime(factuur["factuurdatum"], dayfirst=True)
# factuur = factuur[factuur["status"] == "toegewezen"]
# factuur["jaar"] = factuur["factuurdatum"].dt.year
# factuur["maand"] = factuur["factuurdatum"].dt.month

# fig = px.line(afspraken_all, x='maand', y='aantal', color='jaar', markers=True,
#                   title='Aantal Afspraken per Maand per Jaar')
# fig.update_traces(hovertemplate='<br>Aantal: %{y}<br>')
# fig.update_layout(
#         xaxis_title='Maand', 
#         yaxis_title='Aantal afspraken', 
#         legend_title='Jaar',
#         xaxis=dict(showgrid=True),
#         yaxis=dict(showgrid=True)
#     )


# fig1 = px.line(
#         factuur, 
#         x="maand_naam", 
#         y="totaalbedrag", 
#         color="jaar", 
#         markers=True, 
#         title="Toegewezen facturen per maand (2020-2024)",
#         labels={"maand_naam": "Maand", "totaalbedrag": "Totaalbedrag (€)", "jaar": "Jaar"},
#     )
# fig1.update_traces(hovertemplate='<br>Aantal: %{y}<br>')
# fig1.update_layout(xaxis=dict(showgrid=True), yaxis=dict(showgrid=True))


# # Sidebar voor navigatie
# pagina_keuze = st.sidebar.selectbox("Kies een pagina", ["Aantal Afspraken per Maand", "Andere Pagina"])

# # Aantal afspraken per maand per jaar tellen
# df_groep = afspraken_all.groupby(['jaar', 'maand']).size().reset_index(name='aantal')

# # Sorteer maanden op kalender volgorde
# maand_volgorde = list(calendar.month_name)[1:]  # ['January', 'February', ...]
# df_groep['maand'] = pd.Categorical(df_groep['maand'], categories=maand_volgorde, ordered=True)
# df_groep = df_groep.sort_values(['jaar', 'maand'])

# # Groepeer factuurdata per maand per jaar
# factuur_grouped = factuur.groupby(["jaar", "maand"])["totaalbedrag"].sum().reset_index()
# factuur_grouped["maand_naam"] = factuur_grouped["maand"].apply(lambda x: maand_volgorde[x-1])
# factuur_grouped["maand_naam"] = pd.Categorical(factuur_grouped["maand_naam"], categories=maand_volgorde, ordered=True)
# factuur_grouped = factuur_grouped.sort_values(["maand", "jaar"])

# # Pagina Afspraken
# if pagina_keuze == "Aantal Afspraken per Maand":
#     st.title("Aantal Afspraken per Maand per Jaar")
#     geselecteerde_maanden = st.select_slider("Selecteer maanden", options=maand_volgorde, value=(maand_volgorde[0], maand_volgorde[-1]))
#     maand_start, maand_einde = maand_volgorde.index(geselecteerde_maanden[0]), maand_volgorde.index(geselecteerde_maanden[1])
#     geselecteerde_maanden_namen = maand_volgorde[maand_start:maand_einde + 1]

#     df_groep_filtered = df_groep[df_groep['maand'].isin(geselecteerde_maanden_namen)]
#     factuur_grouped_filtered = factuur_grouped[factuur_grouped["maand_naam"].isin(geselecteerde_maanden_namen)]

#     st.plotly_chart(df_groep_filtered)
#     st.plotly_chart(factuur_grouped_filtered)

# # Andere pagina
# if pagina_keuze == "Andere Pagina":
#     st.title("Andere Pagina")
