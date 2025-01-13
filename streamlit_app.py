import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit as st            
import pandas as pd               
import folium                     
from folium.plugins import MarkerCluster  
from streamlit_folium import st_folium    
import seaborn as sns
import matplotlib.pyplot as plt
import geopandas as gpd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.title("Accidents de la route en 2023")

st.markdown("""
Les données utilisées proviennent de **l'INSEE** et concernent les **accidents de la route en France en 2023**. Elles sont organisées de la façon suivante :

### 📂 Caractéristiques (caract-2023.csv)
- Ce fichier contient des informations générales sur chaque accident, telles que :
    - **Date** et **heure** de l'accident,
    - **Conditions de luminosité** (lum),
    - **Conditions atmosphériques** (atm),
    - **Type de collision** (col).
- Ces données permettent de comprendre le contexte global dans lequel chaque accident s’est produit.

### 🌍 Lieux (lieux-2023.csv)
- Ce fichier décrit les caractéristiques du lieu de l’accident :
    - **Catégorie de route** (catr),
    - **Profil de la route** (prof),
    - **État de la surface** (surf),
    - **Localisation précise de l’accident** (situ).
- Ces informations sont essentielles pour analyser l’influence de l’environnement sur les accidents.

### 🚗 Véhicules (vehicules-2023.csv)
- Ce fichier recense les informations sur les véhicules impliqués dans chaque accident :
    - **Catégorie du véhicule** (catv),
    - **Point initial du choc** (choc),
    - **Manœuvre réalisée avant l’accident** (manv).

### 👥 Usagers (usagers-2023.csv)
- Ce fichier contient des informations sur les usagers impliqués dans les accidents, incluant :
    - Leur **position dans le véhicule** (place),
    - Leur **catégorie** (catu),
    - Leur **gravité** (grav),
    - Leur **sexe** (sexe).
""")

# Sommaire interactif
st.sidebar.title("Sommaire")
st.sidebar.markdown("""
- [🏠 Introduction](#introduction)
- [📂 Chargement des Données](#chargement-des-données)
- [📝 Description des Variables](#description-des-variables)
- [🌍 Carte Interactive](#carte-interactive)
    - [France](#carte-île-de-france)
    - [Île-de-France](#carte-île-de-france)
- [🔍 Analyse Bivariée](#analyse-bivariée)
- [📊 Évolution Temporelle des Accidents](#evolution-temporelle)
- [📈 Machine Learning](#analyse-bivariée)
""")

st.markdown("## 🏠 Introduction")
st.markdown("""
Les données utilisées proviennent de **l'INSEE** et concernent les **accidents de la route en France en 2023**. Elles sont organisées de la façon suivante :

### 📂 Caractéristiques (caract-2023.csv)
- Ce fichier contient des informations générales sur chaque accident, telles que :
    - **Date** et **heure** de l'accident,
    - **Conditions de luminosité** (lum),
    - **Conditions atmosphériques** (atm),
    - **Type de collision** (col).
- Ces données permettent de comprendre le contexte global dans lequel chaque accident s’est produit.

### 🌍 Lieux (lieux-2023.csv)
- Ce fichier décrit les caractéristiques du lieu de l’accident :
    - **Catégorie de route** (catr),
    - **Profil de la route** (prof),
    - **État de la surface** (surf),
    - **Localisation précise de l’accident** (situ).
- Ces informations sont essentielles pour analyser l’influence de l’environnement sur les accidents.

### 🚗 Véhicules (vehicules-2023.csv)
- Ce fichier recense les informations sur les véhicules impliqués dans chaque accident :
    - **Catégorie du véhicule** (catv),
    - **Point initial du choc** (choc),
    - **Manœuvre réalisée avant l’accident** (manv).

### 👥 Usagers (usagers-2023.csv)
- Ce fichier contient des informations sur les usagers impliqués dans les accidents, incluant :
    - Leur **position dans le véhicule** (place),
    - Leur **catégorie** (catu),
    - Leur **gravité** (grav),
    - Leur **sexe** (sexe).
""")


## Chargement des données
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
    title="Répartition géographique des accidents motorisés par gravité",
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


# Variables disponibles pour l'analyse
variables_disponibles = {
    "plage_horaire": "Plage Horaire",
    "catv": "Catégorie de Véhicules",
    "dep": "Département",
    "jour_semaine": "Jour de la Semaine"
}
st.markdown("## 🔍 Analyse Bivariée")
# Choix de la variable
variable_choisie = st.selectbox(
    "Choisissez une variable pour analyser la gravité des accidents :",
    options=list(variables_disponibles.keys()),
    format_func=lambda x: variables_disponibles[x]
)

# Analyse dynamique
if variable_choisie in ["plage_horaire", "catv", "dep"]:
    # Créer une table de fréquence pour la heatmap
    heatmap_data = pd.crosstab(
        accidents_motorises_idf[variable_choisie],
        accidents_motorises_idf['grav_desc'],
        normalize='index'
    )

    # Trier les plages horaires si la variable choisie est "plage_horaire"
    if variable_choisie == "plage_horaire":
        heatmap_data = heatmap_data.reindex(["Matin (6h-12h)", "Après-midi (12h-18h)", "Soir (18h-6h)"])

    # Si l'utilisateur choisit "dep", afficher les noms des départements
    if variable_choisie == "dep":
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

    # Affichage de la heatmap
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".2f",
        cmap="YlOrRd",
        cbar_kws={'label': 'Proportion'},
        linewidths=0.5,
        ax=ax
    )
    ax.set_title(f"Répartition des Accidents par Gravité et {variables_disponibles[variable_choisie]}", fontsize=14)
    ax.set_xlabel("Gravité", fontsize=12)
    ax.set_ylabel(variables_disponibles[variable_choisie], fontsize=12)
    plt.xticks(fontsize=10, rotation=45)
    plt.yticks(fontsize=10)
    st.pyplot(fig)

elif variable_choisie == "jour_semaine":
    # Réorganiser les jours dans l'ordre français
    jours_ordre = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

    # Préparer les données pour le graphique empilé
    stacked_data = pd.crosstab(
        accidents_motorises_idf['jour_semaine'],
        accidents_motorises_idf['grav_desc']
    )
    stacked_data = stacked_data.reindex(jours_ordre)  # Réorganiser les jours

    # Palette de couleurs
    colors = ["#ffcc66", "#ff9966", "#FFFF00", "#ff3333"]

    # Graphique empilé
    st.subheader("Distribution des Accidents par Jour de la Semaine")
    fig, ax = plt.subplots(figsize=(12, 6))
    stacked_data.plot(
        kind='bar',
        stacked=True,
        figsize=(12, 6),
        color=colors,
        ax=ax
    )

    # Personnaliser le graphique
    ax.set_title("Distribution des Accidents par Jour de la Semaine", fontsize=16, fontweight='bold')
    ax.set_xlabel("Jour de la Semaine", fontsize=14)
    ax.set_ylabel("Nombre d'Accidents", fontsize=14)
    ax.legend(
        title="Gravité",
        fontsize=12,
        title_fontsize=14,
        loc='upper left',
        bbox_to_anchor=(1.05, 1)
    )
    plt.xticks(fontsize=12, rotation=45)
    plt.yticks(fontsize=12)
    st.pyplot(fig)

# Evolution temporelle des accidents
st.markdown("## 📊 Évolution Temporelle des Accidents")

# Préparer les données temporelles
time_analysis = accidents_motorises.groupby(['mois', 'jour']).size().reset_index(name='count')
time_analysis['date'] = pd.to_datetime(
    {'year': 2023, 'month': time_analysis['mois'], 'day': time_analysis['jour']}
)

# Trier les données par date
time_analysis = time_analysis.sort_values('date')

# Créer le graphique avec Plotly
fig = px.line(
    time_analysis,
    x='date',
    y='count',
    title="Évolution temporelle des accidents en 2023",
    labels={'date': 'Date', 'count': "Nombre d'accidents"},
    markers=True,  # Ajouter des marqueurs
    line_shape='spline',  # Lissage de la courbe
    color_discrete_sequence=["#FF5733"]  # Couleur vibrante
)


# Mettre à jour le design du graphique
fig.update_layout(
    title=dict(
        text="Évolution temporelle des accidents en 2023",
        font=dict(size=20, color="#333", family="Arial")
    ),
    xaxis=dict(
        title="Date",
        showgrid=True,
        gridcolor="rgba(200,200,200,0.3)",
        tickformat="%b %d",  # Afficher le mois et le jour
        tickangle=-45
    ),
    yaxis=dict(
        title="Nombre d'accidents",
        showgrid=True,
        gridcolor="rgba(200,200,200,0.3)"
    ),
    plot_bgcolor="white",  # Arrière-plan blanc
    margin=dict(l=50, r=50, t=80, b=50),
    hovermode="x unified"  # Info survol unifiée
)

# Afficher le graphique
st.plotly_chart(fig, use_container_width=True)


st.markdown("### ☁️ Nuage de mots : Analyse des Départements")

# Vérifier qu'il y a des données dans la colonne 'dep'
if not accidents_motorises['dep'].isna().all():
    # Remplacer les codes des départements par leur nom
    department_names = {
        75: "Paris",
        77: "Seine-et-Marne",
        78: "Yvelines",
        91: "Essonne",
        92: "Hauts-de-Seine",
        93: "Seine-Saint-Denis",
        94: "Val-de-Marne",
        95: "Val-d'Oise"
    }
    accidents_motorises['dep_name'] = accidents_motorises['dep'].map(department_names)

    # Supprimer les départements non inclus dans le mapping
    accidents_motorises = accidents_motorises.dropna(subset=['dep_name'])

    # Compter les occurrences de chaque département
    dep_counts = accidents_motorises['dep_name'].value_counts()

    # Créer une chaîne de texte pondérée pour le Word Cloud
    text_data = " ".join([f"{dep} " * count for dep, count in dep_counts.items()])

    # Créer le Word Cloud
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color="white",
        colormap="plasma",
        max_words=100,
        contour_color="black"
    ).generate(text_data)

    # Afficher le Word Cloud
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")  # Pas de bordure
    ax.set_title("Nuage de mots des départements d'Ile de France les plus accidentés", fontsize=16, fontweight="bold")
    st.pyplot(fig)
else:
    st.warning("Pas de données suffisantes pour créer un nuage de mots des départements.")



st.markdown("## 📈 Machine Learning")
