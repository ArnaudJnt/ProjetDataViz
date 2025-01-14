import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import seaborn as sns
import matplotlib.pyplot as plt
import geopandas as gpd
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard - Accidents 2023", layout="wide")

# Titre principal
st.markdown(
    """
    <div style="background-color:#ffcc66;padding:15px;border-radius:10px;text-align:center;">
    <h1 style="color:#333;"> Tableau de bord : Accidents de la route 2023 </h1>
    </div>
    """, unsafe_allow_html=True
)

st.sidebar.title("Sommaire")
st.sidebar.markdown("""
- [🏠 Introduction](#introduction)
- [📂 Chargement des Données](#chargement-des-donnees)
- [📝 Description des Variables](#description-des-variables)
- [🌍 Carte Interactive](#carte-interactive)
- [🔍 Analyse Descriptive](#analyse-descriptive)
- [📊 Évolution Temporelle des Accidents](#evolution-temporelle-des-accidents)
""", unsafe_allow_html=True)

st.markdown("<a id='introduction'></a>", unsafe_allow_html=True)
st.markdown("## 🏠 Introduction")
st.markdown("""
Les données utilisées proviennent de **l'INSEE** et concernent les **accidents de la route en France en 2023**. Elles sont organisées de la façon suivante :

📂 Caractéristiques (caract-2023.csv)
- Ce fichier contient des informations générales sur chaque accident 

🌍 Lieux (lieux-2023.csv)
- Ce fichier décrit les caractéristiques du lieu de l’accident 

🚗 Véhicules (vehicules-2023.csv)
- Ce fichier recense les informations sur les véhicules impliqués dans chaque accident 

👥 Usagers (usagers-2023.csv)
- Ce fichier contient des informations sur les usagers impliqués dans les accidents
""")


## Chargement des données
st.markdown("<a id='chargement-des-donnees'></a>", unsafe_allow_html=True)
st.markdown("## 📂 Chargement des Données")
# Utiliser le cache pour optimiser les performances lors du chargement des fichiers
@st.cache_data
def load_data(file_path):
    """Charge un fichier CSV donné."""
    try:
        return pd.read_csv(file_path, sep=';', decimal=',')
    except FileNotFoundError:
        st.error(f"Le fichier {file_path} est introuvable.")
        return None

# Définir les chemins relatifs vers les fichiers
caract_file_path = "data/caract-2023.csv"
lieux_file_path = "data/lieux-2023.csv"
vehicules_file_path = "data/vehicules-2023.csv"
usagers_file_path = "data/usagers-2023.csv"

caract_df = load_data(caract_file_path)
lieux_df = load_data(lieux_file_path)
vehicules_df = load_data(vehicules_file_path)
usagers_df = load_data(usagers_file_path)

# Vérifier que tous les fichiers ont été chargés
if caract_df is not None and lieux_df is not None and vehicules_df is not None and usagers_df is not None:
    ## Fusion des bases de données
    merged_df = caract_df.merge(lieux_df, on='Num_Acc')
    merged_df = merged_df.merge(vehicules_df, on='Num_Acc')
    merged_df = merged_df.merge(usagers_df, on='Num_Acc')

    # Supprimer les doublons
    merged_df = merged_df.drop_duplicates()

    # Définir les codes des véhicules motorisés
    codes_motorises = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14]

    # Filtrer les données pour conserver uniquement les véhicules motorisés
    accidents_motorises = merged_df[merged_df['catv'].isin(codes_motorises)]

    # Conversion des colonnes en types numériques
    accidents_motorises['lat'] = pd.to_numeric(accidents_motorises['lat'], errors='coerce')
    accidents_motorises['long'] = pd.to_numeric(accidents_motorises['long'], errors='coerce')
    accidents_motorises['dep'] = pd.to_numeric(accidents_motorises['dep'], errors='coerce')
    accidents_motorises['com'] = pd.to_numeric(accidents_motorises['com'], errors='coerce')

    # Affichage des données fusionnées
    st.write("Aperçu de la base de données :")
    st.dataframe(merged_df.head())

else:
    st.error("Un ou plusieurs fichiers n'ont pas pu être chargés. Vérifiez leur emplacement ou leur contenu.")

# Réduire la base de données de 50 % aléatoirement
accidents_motorises = accidents_motorises.sample(frac=0.5, random_state=42)

st.markdown("<a id='description-des-variables'></a>", unsafe_allow_html=True)
st.markdown("## 📝 Description des Variables")
# Dictionnaire contenant les descriptions des variables pour chaque fichier
descriptions = {
    "Caractéristiques (caract-2023.csv)": {
        "Num_Acc": "Identifiant unique de l'accident.",
        "an": "Année de l'accident.",
        "mois": "Mois de l'accident.",
        "jour": "Jour de l'accident.",
        "hrmn": "Heure et minute de l'accident (exemple : '13h45').",
        "lum": "Conditions de luminosité :\n"
               "1 : Plein jour.\n"
               "2 : Crépuscule ou aube.\n"
               "3 : Nuit sans éclairage.\n"
               "4 : Nuit avec éclairage non allumé.\n"
               "5 : Nuit avec éclairage allumé.",
        "agg": "L'accident a-t-il eu lieu en agglomération ?\n"
               "1 : Oui.\n"
               "2 : Non.",
        "int": "Type d'intersection :\n"
               "1 : Hors intersection.\n"
               "2 : Intersection en X.\n"
               "3 : Intersection en T.\n"
               "4 : Intersection en Y.\n"
               "5 : Rond-point.\n"
               "6 : Place.\n"
               "7 : Autre intersection.",
        "atm": "Conditions atmosphériques :\n"
               "1 : Normales.\n"
               "2 : Pluie légère.\n"
               "3 : Pluie forte.\n"
               "4 : Neige ou grêle.\n"
               "5 : Brouillard ou fumée.\n"
               "6 : Vent fort ou tempête.\n"
               "7 : Temps éblouissant.\n"
               "8 : Temps couvert.\n"
               "9 : Autres.",
        "col": "Type de collision :\n"
               "1 : Deux véhicules - frontale.\n"
               "2 : Deux véhicules - par l'arrière.\n"
               "3 : Deux véhicules - par le côté.\n"
               "4 : Trois véhicules ou plus - en chaîne.\n"
               "5 : Trois véhicules ou plus - collisions multiples.\n"
               "6 : Autre collision.",
        "dep": "Département où l'accident a eu lieu.",
        "com": "Commune où l'accident a eu lieu.",
        "adr": "Adresse approximative de l'accident."
    },
    "Lieux (lieux-2023.csv)": {
        "Num_Acc": "Identifiant unique de l'accident.",
        "catr": "Catégorie de route :\n"
                "1 : Autoroute.\n"
                "2 : Route nationale.\n"
                "3 : Route départementale.\n"
                "4 : Voie communale.\n"
                "5 : Hors réseau public.\n"
                "6 : Parking.\n"
                "7 : Autres.",
        "voie": "Numéro de voie.",
        "v1": "Numéro de l'indice de lieu (précision géographique).",
        "v2": "Numéro de l'indice de lieu (précision géographique).",
        "circ": "Régime de circulation :\n"
                "1 : À sens unique.\n"
                "2 : Bidirectionnelle.\n"
                "3 : Avec voies spécialisées.",
        "nbv": "Nombre de voies.",
        "prof": "Profil de la route :\n"
                "1 : Plat.\n"
                "2 : Pente.\n"
                "3 : Sommet de côte.\n"
                "4 : Bas de côte.",
        "plan": "Tracé en plan :\n"
                "1 : Rectiligne.\n"
                "2 : En courbe à gauche.\n"
                "3 : En courbe à droite.\n"
                "4 : En S.",
        "surf": "État de la surface :\n"
                "1 : Normale.\n"
                "2 : Mouillée.\n"
                "3 : En flaques.\n"
                "4 : Verglacée.\n"
                "5 : Boue.\n"
                "6 : Neige.\n"
                "7 : Sable ou gravillons.\n"
                "8 : Huile.\n"
                "9 : Autres.",
        "infra": "Présence d'infrastructure particulière :\n"
                 "0 : Aucune.\n"
                 "1 : Souterrain.\n"
                 "2 : Pont.\n"
                 "3 : Bretelle.\n"
                 "4 : Voie ferrée.\n"
                 "5 : Carrefour aménagé.\n"
                 "6 : Zone piétonne.\n"
                 "7 : Zone de péage.",
        "situ": "Localisation de l'accident :\n"
                "1 : Sur chaussée.\n"
                "2 : Sur bande d'arrêt d'urgence.\n"
                "3 : Sur accotement.\n"
                "4 : Sur trottoir.\n"
                "5 : Sur piste cyclable."
    },
    "Véhicules (vehicules-2023.csv)": {
        "Num_Acc": "Identifiant unique de l'accident.",
        "id_vehicule": "Identifiant unique du véhicule.",
        "catv": "Catégorie du véhicule :\n"
                "1 : Vélo.\n"
                "2 : Cyclomoteur.\n"
                "3 : Moto < 50 cm³.\n"
                "4 : Moto > 50 cm³.\n"
                "5 : VL seul.\n"
                "6 : VL + remorque.\n"
                "7 : VU seul.\n"
                "8 : VU + remorque.\n"
                "9 : PL seul 3,5T < PTAC < 7,5T.\n"
                "10 : PL > 7,5T.\n"
                "11 : Bus.\n"
                "12 : Tramway.\n"
                "13 : Train.\n"
                "14 : Engin spécial.\n"
                "15 : Autre.",
        "obs": "Obstacle fixe heurté.",
        "obsm": "Obstacle mobile heurté.",
        "choc": "Point initial du choc :\n"
                "1 : Avant.\n"
                "2 : Avant droit.\n"
                "3 : Avant gauche.\n"
                "4 : Arrière.\n"
                "5 : Arrière droit.\n"
                "6 : Arrière gauche.",
        "manv": "Manœuvre principale avant l'accident."
    },
    "Usagers (usagers-2023.csv)": {
        "Num_Acc": "Identifiant unique de l'accident.",
        "id_vehicule": "Identifiant unique du véhicule associé.",
        "place": "Position dans le véhicule (conducteur, passager, etc.).",
        "catu": "Catégorie d'usager :\n"
                "1 : Conducteur.\n"
                "2 : Passager.\n"
                "3 : Piéton.",
        "grav": "Gravité de l'accident pour la personne :\n"
                "1 : Indemne.\n"
                "2 : Blessé léger.\n"
                "3 : Blessé hospitalisé.\n"
                "4 : Tué.",
        "sexe": "Sexe de l'usager :\n"
                "1 : Masculin.\n"
                "2 : Féminin.",
        "trajet": "Raison du déplacement :\n"
                  "1 : Domicile-travail.\n"
                  "2 : Domicile-école.\n"
                  "3 : Déplacement professionnel.\n"
                  "4 : Loisirs.\n"
                  "5 : Autres.",
        "secu": "Utilisation des équipements de sécurité (ceinture, casque, etc.)."
    }
}

# Interface utilisateur

# Sélection du fichier
file_choice = st.selectbox(
    "Choisissez un fichier pour voir toutes ses variables :",
    options=list(descriptions.keys()),
    index=0
)

# Afficher les descriptions
if file_choice:
    st.subheader(f"Descriptions des variables pour : {file_choice}")
    for variable, description in descriptions[file_choice].items():
        st.markdown(f"**{variable}** : {description}")

st.markdown("<a id='carte-interactive'></a>", unsafe_allow_html=True)
st.markdown("## 🌍 Carte Interactive")
st.markdown("### Carte de France")
# Ajout de la description de la gravité
gravite_dict = {
    1: "Blessé léger",
    2: "Indemne",
    3: "Blessé hospitalisé",
    4: "Tué"
}
accidents_motorises['grav_desc'] = accidents_motorises['grav'].map(gravite_dict)

# Filtrage des lignes avec des valeurs valides
accidents_motorises = accidents_motorises.dropna(subset=['lat', 'long', 'grav_desc'])

# Création de la carte
fig = px.scatter_mapbox(
    accidents_motorises,
    lat='lat',
    lon='long',
    color='grav_desc',
    color_discrete_map={
        "Indemne": "#0080ff",
        "Blessé léger": "#ffff66",
        "Blessé hospitalisé": "#ff9933",
        "Tué": "#ff3300"
    },
    mapbox_style="open-street-map",
    zoom=12,
    height=800,
    hover_name='grav_desc'
)

fig.update_layout(legend_title="Gravité")

# Affichage de la carte dans Streamlit
st.plotly_chart(fig, use_container_width=True)

# Liste des départements d'Île-de-France
idf_departments = {
    75: "Paris",
    77: "Seine-et-Marne",
    78: "Yvelines",
    91: "Essonne",
    92: "Hauts-de-Seine",
    93: "Seine-Saint-Denis",
    94: "Val-de-Marne",
    95: "Val-d'Oise"
}

# Interface utilisateur
st.markdown("### Carte Île-de-France")

# Menu pour sélectionner un département
selected_dep = st.selectbox(
    "Choisissez un département :",
    options=list(idf_departments.keys()),
    format_func=lambda x: f"{idf_departments[x]} ({x})"
)

# Filtrer les données pour le département sélectionné
filtered_data = accidents_motorises[accidents_motorises["dep"] == selected_dep]

# Fonction pour générer la carte (cachée pour éviter le recalcul)
@st.cache_data
def create_map(filtered_data):
    # Initialiser une carte centrée sur le département sélectionné
    m = folium.Map(
        location=[filtered_data["lat"].mean(), filtered_data["long"].mean()],
        zoom_start=10
    )

    # Ajouter des marqueurs pour les accidents
    for _, row in filtered_data.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["long"]],
            radius=6,
            color="red" if row["grav"] == 4 else "orange" if row["grav"] == 3 else "blue",
            fill=True,
            fill_opacity=0.7,
            popup=f"Gravité : {row['grav']}"
        ).add_to(m)
    return m

# Créer la carte uniquement si des données existent
if not filtered_data.empty:
    accident_map = create_map(filtered_data)
    st_folium(accident_map, width=800, height=500)
else:
    st.warning("Aucune donnée disponible pour le département sélectionné.")


# Ajouter une description de la gravité
gravite_dict = {
    1: "Indemne",
    2: "Blessé léger",
    3: "Blessé hospitalisé",
    4: "Tué"
}
accidents_motorises['grav_desc'] = accidents_motorises['grav'].map(gravite_dict)

# Liste des départements d'Île-de-France
idf_departments = [75, 77, 78, 91, 92, 93, 94, 95]

# Filtrer uniquement les départements d'Île-de-France
accidents_motorises_idf = accidents_motorises[accidents_motorises['dep'].isin(idf_departments)]

# Ajouter une colonne pour les plages horaires
def categorize_time(hour):
    if 6 <= hour < 12:
        return "Matin (6h-12h)"
    elif 12 <= hour < 18:
        return "Après-midi (12h-18h)"
    else:
        return "Soir (18h-6h)"
accidents_motorises_idf['heure'] = accidents_motorises_idf['hrmn'].str.split(':').str[0].astype(int)
accidents_motorises_idf['plage_horaire'] = accidents_motorises_idf['heure'].apply(categorize_time)

# Ajouter une colonne avec les jours de la semaine
accidents_motorises_idf['jour_semaine_en'] = pd.to_datetime(
    accidents_motorises_idf[['an', 'mois', 'jour']].rename(columns={'an': 'year', 'mois': 'month', 'jour': 'day'})
).dt.day_name()

# Traduire les jours de la semaine en français
jours_traduction = {
    "Monday": "lundi",
    "Tuesday": "mardi",
    "Wednesday": "mercredi",
    "Thursday": "jeudi",
    "Friday": "vendredi",
    "Saturday": "samedi",
    "Sunday": "dimanche"
}
accidents_motorises_idf['jour_semaine'] = accidents_motorises_idf['jour_semaine_en'].map(jours_traduction)


st.markdown("<a id='analyse-descriptive'></a>", unsafe_allow_html=True)
st.markdown("## 🔍 Analyse Descriptive")

# Dictionnaire pour l'affichage des variables
variables_disponibles = {
    "plage_horaire": "Plage Horaire",
    "catv": "Catégorie de Véhicules",
    "dep": "Département",
    "jour_semaine": "Jour de la Semaine",
    "pie_grav": "Camembert (Répartition par Gravité)"
}

# 5. Camembert (Répartition par Gravité)
st.markdown("### Répartition des Accidents par Gravité")
grav_count = accidents_motorises['grav_desc'].value_counts().reset_index()
grav_count.columns = ['Gravité', 'Nombre d\'accidents']

fig = px.pie(
    grav_count,
    values='Nombre d\'accidents',
    names='Gravité',
    color_discrete_sequence=px.colors.sequential.RdBu,
    template="presentation",
    hole=0.4  # Donut chart
)
st.plotly_chart(fig, use_container_width=True)
# Analyse des différentes options (sans menu déroulant)

# 1. Plage Horaire
st.markdown("### Répartition des Accidents par Plage Horaire et Gravité")
# Création des données pour la heatmap
# Création des données pour la heatmap
heatmap_data = pd.crosstab(
    accidents_motorises_idf["plage_horaire"],
    accidents_motorises_idf["grav_desc"],
    normalize='index'
)

heatmap_data = heatmap_data.reindex(["Matin (6h-12h)", "Après-midi (12h-18h)", "Soir (18h-6h)"])

# Création de la heatmap avec Plotly
fig = px.imshow(
    heatmap_data,
    text_auto=".2f",
    labels=dict(x="Gravité", y="Plage Horaire", color="Proportion"),
    color_continuous_scale="YlOrRd"
)

# Personnalisation du thème noir
fig.update_layout(
    title = " ",
    xaxis=dict(tickangle=-45, title_font=dict(size=14, color='white'), tickfont=dict(color='white')),
    yaxis=dict(title_font=dict(size=14, color='white'), tickfont=dict(color='white')),
    plot_bgcolor="black",
    paper_bgcolor="black",
    font=dict(color="white")
)

# Affichage dans Streamlit
st.plotly_chart(fig, use_container_width=True)


# 3. Département
# Création des données pour la heatmap
st.markdown("### Répartition des Accidents par Département")
heatmap_data = pd.crosstab(
    accidents_motorises_idf["dep"],
    accidents_motorises_idf["grav_desc"],
    normalize='index'
)

# Renommer les départements
heatmap_data.index = heatmap_data.index.map({
    75: "Paris",
    77: "Seine-et-Marne",
    78: "Yvelines",
    91: "Essonne",
    92: "Hauts-de-Seine",
    93: "Seine-Saint-Denis",
    94: "Val-de-Marne",
    95: "Val-d'Oise"
})

# Création de la heatmap avec Plotly
fig = px.imshow(
    heatmap_data,
    text_auto=".2f",  # Formater les valeurs avec 2 décimales
    labels=dict(x="Gravité", y="Département", color="Proportion"),
    color_continuous_scale="YlOrRd"
)

# Personnalisation du thème noir
fig.update_layout(
    title=" ",  # Supprime le titre
    xaxis=dict(tickangle=-45, title_font=dict(size=14, color='white'), tickfont=dict(color='white')),
    yaxis=dict(title_font=dict(size=14, color='white'), tickfont=dict(color='white')),
    plot_bgcolor="black",  # Fond noir pour la zone des graphiques
    paper_bgcolor="black",  # Fond noir pour tout le fond du graphique
    font=dict(color="white")  # Texte en blanc
)

# Affichage dans Streamlit
st.plotly_chart(fig, use_container_width=True)




# Evolution temporelle des accidents
st.markdown("<a id='evolution-temporelle-des-accidents'></a>", unsafe_allow_html=True)
st.markdown("## 📊 Évolution Temporelle des Accidents")

# 4. Jour de la Semaine
st.markdown("### Distribution des Accidents par Jour de la Semaine")

# Réorganiser les jours de la semaine
jours_ordre = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
stacked_data = pd.crosstab(
    accidents_motorises_idf["jour_semaine"],
    accidents_motorises_idf["grav_desc"]
)
stacked_data = stacked_data.reindex(jours_ordre)

colors = ["#ffcc66", "#ff9966", "#FFFF00", "#ff3333"]

# Création de la figure
fig, ax = plt.subplots(figsize=(12, 6))

# Définir le fond noir
fig.patch.set_facecolor('black')  # Fond noir pour la figure
ax.set_facecolor('black')  # Fond noir pour le graphique

# Traçage des données empilées
stacked_data.plot(
    kind='bar',
    stacked=True,
    figsize=(12, 6),
    color=colors,
    ax=ax
)

# Personnalisation des titres et axes
ax.set_title(" ", fontsize=16, fontweight='bold', color='white')
ax.set_xlabel("Jour de la Semaine", fontsize=14, color='white')
ax.set_ylabel("Nombre d'Accidents", fontsize=14, color='white')
ax.legend(
    title="Gravité",
    fontsize=12,
    title_fontsize=14,
    loc='upper left',
    bbox_to_anchor=(1.05, 1),
    labelcolor='white'  # Couleur des labels de légende
)

# Ajustement des couleurs des ticks
plt.xticks(fontsize=12, rotation=45, color='white')
plt.yticks(fontsize=12, color='white')

# Affichage dans Streamlit
st.pyplot(fig)


st.markdown("### Evolution Temporelle des Accidents en 2023 ")

# Préparer les données temporelles
time_analysis = accidents_motorises.groupby(['mois', 'jour']).size().reset_index(name='count')
time_analysis['date'] = pd.to_datetime(
    {'year': 2023, 'month': time_analysis['mois'], 'day': time_analysis['jour']}
)

# Trier les données par date
time_analysis = time_analysis.sort_values('date')

## Créer le graphique avec Plotly
fig = px.line(
    time_analysis,
    x='date',
    y='count',
    title=" ",
    labels={'date': 'Date', 'count': "Nombre d'accidents"},
    markers=True,  # Ajouter des marqueurs
    line_shape='spline',  # Lissage de la courbe
    color_discrete_sequence=["#FF5733"]  # Couleur vibrante
)

# Mettre à jour le design du graphique
fig.update_layout(
    title=dict(
        text=" ",
        font=dict(size=20, color='#f7f7f7', family="Arial")  # Titre en blanc
    ),
    xaxis=dict(
        title="Date",
        showgrid=True,
        gridcolor="rgba(200,200,200,0.3)",  # Couleur discrète pour les lignes de la grille
        tickformat="%b %d",  # Afficher le mois et le jour
        tickangle=-45,
        title_font=dict(color="white"),  # Texte de l'axe X en blanc
        tickfont=dict(color="white")  # Ticks en blanc
    ),
    yaxis=dict(
        title="Nombre d'accidents",
        showgrid=True,
        gridcolor="rgba(200,200,200,0.3)",  # Couleur discrète pour les lignes de la grille
        title_font=dict(color="white"),  # Texte de l'axe Y en blanc
        tickfont=dict(color="white")  # Ticks en blanc
    ),
    plot_bgcolor="#303030",  # Fond du graphique (gris foncé pour s'aligner sur le thème sombre)
    paper_bgcolor="#303030",  # Fond de la figure (même couleur que le Dashboard)
    font=dict(color="white"),  # Couleur du texte
    margin=dict(l=50, r=50, t=80, b=50),
    hovermode="x unified"  # Info survol unifiée
)

# Afficher le graphique
st.plotly_chart(fig, use_container_width=True)


data = accidents_motorises_idf['heure']

st.markdown("### Distribution des Accidents par Heure de la Journée ")

# Créer un histogramme interactif avec Plotly
fig = px.histogram(
    data, 
    x=data, 
    nbins=24,  # 24 bins pour les heures de la journée
    title=" ",
    labels={'x': 'Heure', 'y': 'Fréquence'},  # Étiquettes des axes
    color_discrete_sequence=["#FF5733"]  # Couleur personnalisée
)

# Ajouter des options de style
fig.update_layout(
    title=dict(
        font=dict(size=20, family='Arial', color='#f7f7f7')
    ),
    xaxis=dict(
        title="Heure",
        tickmode='linear',
        tick0=0,
        dtick=2  # Affiche une graduation toutes les deux heures
    ),
    yaxis=dict(title="Fréquence"),
    bargap=0.1  # Espacement entre les barres
)

# Afficher avec Streamlit
st.plotly_chart(fig)


monthly_data = accidents_motorises.groupby(['mois', 'grav_desc']).size().reset_index(name='count')
fig = px.line(
    monthly_data,
    x='mois',
    y='count',
    color='grav_desc',
    title=" ",
    markers=True,
    line_shape='spline',
    color_discrete_sequence=px.colors.qualitative.Dark24
)

fig.update_layout(
    title=dict(
        font=dict(size=20, family='Arial', color='#f7f7f7')
    )
)
st.plotly_chart(fig, use_container_width=True)


