import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import datetime

# Configurazione base
st.set_page_config(layout="wide")
st.title("🏀 Sessione di Tiri - Allenamento Basket")

# --- Costanti ---
ROSTER = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
ZONES = {
    "Angolo sinistro": ((0, 100), (300, 400)),
    "Ala sinistra": ((100, 200), (300, 400)),
    "Centro sinistra": ((200, 250), (300, 400)),
    "Centro": ((250, 350), (300, 400)),
    "Centro destra": ((350, 400), (300, 400)),
    "Ala destra": ((400, 500), (300, 400)),
    "Angolo destro": ((500, 600), (300, 400)),
}

# Stato sessione
if "session_data" not in st.session_state:
    st.session_state.session_data = {}
if "current_zone" not in st.session_state:
    st.session_state.current_zone = None

# --- 1. Crea una nuova sessione ---
st.subheader("1. Definisci nuova sessione")

session_date = st.date_input("📅 Data della sessione", datetime.date.today())
selected_players = st.multiselect("👥 Giocatori presenti", ROSTER)

if selected_players:
    st.success(f"Hai selezionato: {', '.join(selected_players)}")
else:
    st.warning("Seleziona almeno un giocatore per iniziare.")

# --- 2. Campo interattivo per scelta zona ---
st.subheader("2. Clicca sulla zona di tiro")

court_img = Image.open("/workspaces/basket-tiri-00/campo.jpg")

canvas_result = st_canvas(
    fill_color="rgba(255, 0, 0, 0.3)",
    stroke_width=1,
    background_image=court_img,
    update_streamlit=True,
    height=400,
    width=600,
    drawing_mode="point",
    key="canvas",
)

# Funzione per capire la zona cliccata
def get_clicked_zone(x, y):
    for zone_name, ((x1, x2), (y1, y2)) in ZONES.items():
        if x1 <= x <= x2 and y1 <= y <= y2:
            return zone_name
    return None

# Salva zona cliccata
if canvas_result.json_data is not None:
    for obj in canvas_result.json_data["objects"]:
        x = obj["left"]
        y = obj["top"]
        zone = get_clicked_zone(x, y)
        if zone:
            st.success(f"Zona selezionata: {zone}")
            st.session_state.current_zone = zone
        else:
            st.warning("Clic al di fuori delle zone riconosciute.")

# --- 3. Inserimento tiri ---
st.subheader("3. Inserisci tiri effettuati")

if st.session_state.current_zone and selected_players:
    with st.form(key="tiri_form"):
        st.markdown(f"**Zona attiva: `{st.session_state.current_zone}`**")
        player = st.selectbox("Giocatore", selected_players)
        tiri_2pt = st.number_input("✅ Canestri da 2 punti", min_value=0, step=1)
        tiri_3pt = st.number_input("✅ Canestri da 3 punti", min_value=0, step=1)
        tiri_pat = st.number_input("✅ Canestri da 2 punti - Palleggio, arresto e tiro", min_value=0, step=1)

        submitted = st.form_submit_button("💾 Salva tiri")
        if submitted:
            session_key = str(session_date)
            if session_key not in st.session_state.session_data:
                st.session_state.session_data[session_key] = {}

            player_data = st.session_state.session_data[session_key].setdefault(player, {})
            zone_data = player_data.setdefault(st.session_state.current_zone, {"2pt": 0, "3pt": 0, "pat": 0})
            zone_data["2pt"] += tiri_2pt
            zone_data["3pt"] += tiri_3pt
            zone_data["pat"] += tiri_pat

            st.success("Dati salvati! ✅")
else:
    st.info("Seleziona una zona e un giocatore per inserire i tiri.")

# --- 4. Visualizza dati salvati ---
st.subheader("📊 Dati della sessione")

if st.session_state.session_data:
    session_key = str(session_date)
    if session_key in st.session_state.session_data:
        for player, zones in st.session_state.session_data[session_key].items():
            st.markdown(f"### 👤 {player}")
            for zone, stats in zones.items():
                st.markdown(f"- **{zone}** → 2PT: {stats['2pt']} | 3PT: {stats['3pt']} | PAT: {stats['pat']}")
    else:
        st.info("Nessun dato ancora per questa sessione.")
