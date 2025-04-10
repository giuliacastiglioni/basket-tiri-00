import streamlit as st
import datetime
import tempfile
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
from fpdf import FPDF
from io import BytesIO

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

# Funzione per disegnare metà campo
def draw_half_court(ax, line_width=2, line_color='black'):
    ax.plot([-8, 8], [0, 0], color=line_color, lw=line_width)  # Linea metà campo
    ax.plot([-8, -8], [-2, 13], color=line_color, lw=line_width)  # Linea laterale sinistra
    ax.plot([8, 8], [-2, 13], color=line_color, lw=line_width)  # Linea laterale destra
    ax.plot([-8, 8], [13, 13], color=line_color, lw=line_width)  # Linea di fondo
    ax.plot([2, 2], [13, 6.5], color=line_color, lw=line_width)  # Linea laterale destra
    ax.plot([-2, -2], [13, 6.5], color=line_color, lw=line_width)  # Linea laterale sinistra
    ax.plot([-2, 2], [6.5, 6.5], color=line_color, lw=line_width)  # Linea centrale
    ax.plot([6.75, 6.75], [10.2, 13], color=line_color, lw=line_width)  # linea laterale destra
    ax.plot([-6.75, -6.75], [10.2, 13], color=line_color, lw=line_width)  # linea laterale destra
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
# Cerchio di centro campo
    circle = plt.Circle((0, 6.5), 2, color=line_color, fill=False, lw=line_width)
    ax.add_patch(circle)

    # Aggiungi il semicircolo (arco di tiro)
    semicircle = Arc((0, 10.5), width=13.5, height=13.5, angle=180, theta1=0, theta2=180,
                     color=line_color, lw=line_width)
    ax.add_patch(semicircle)

# Posizioni dei tiri
shooting_positions = [(-7.2, 12), (-7, 9), (-4, 5.5), (0, 5.5), (4, 5.5), (7, 9), (7.2, 12)]
position_names = ["Angolo sx", "Ala sx", "Centro sx", "Centro", "Centro dx", "Ala dx", "Angolo dx"]

# Disegna il campo
fig, ax = plt.subplots(figsize=(12, 10))
draw_half_court(ax)
x_coords, y_coords = zip(*shooting_positions)
ax.scatter(x_coords, y_coords, color='red', s=150, label="Posizioni di tiro", zorder=5)

for i, (x, y) in enumerate(shooting_positions):
    ax.text(x, y + 0.4, position_names[i], ha='center', color='blue', fontsize=18, fontweight='bold')

st.pyplot(fig)

# --- 2. Seleziona una zona di tiro ---
st.subheader("2. Seleziona la zona di tiro")
zones = ['Angolo sinistro', 'Ala sinistra', 'Centro sinistra', 'Centro', 'Centro destra', 'Ala destra', 'Angolo destro']
zone_selected = st.radio("Seleziona una zona di tiro", zones)

if zone_selected:
    st.session_state.current_zone = zone_selected  # Aggiorna la zona selezionata
    st.success(f"Zona selezionata: {zone_selected}")
else:
    st.warning("Seleziona una zona per continuare.")

# --- 3. Inserisci i tiri ---
st.subheader("3. Inserisci tiri effettuati")

if st.session_state.current_zone and selected_players:
    with st.form(key="tiri_form"):
        st.markdown(f"**Zona attiva: `{st.session_state.current_zone}`**")
        player = st.selectbox("Giocatore", selected_players)
        tiri_totali_zona = st.number_input("✅ Tiri totali nella zona", min_value=0, step=1)
        tiri_2pt = st.number_input("✅ Canestri da 2 punti", min_value=0, step=1)
        tiri_3pt = st.number_input("✅ Canestri da 3 punti", min_value=0, step=1)
        tiri_pat = st.number_input("✅ Canestri da 2 punti - Palleggio, arresto e tiro", min_value=0, step=1)

        submitted = st.form_submit_button("💾 Salva tiri")
        if submitted:
            session_key = str(session_date)
            if session_key not in st.session_state.session_data:
                st.session_state.session_data[session_key] = {}

            player_data = st.session_state.session_data[session_key].setdefault(player, {})
            zone_data = player_data.setdefault(st.session_state.current_zone, {"totali": 0,"2pt": 0, "3pt": 0, "pat": 0})
            zone_data["totali"] += tiri_totali_zona
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
                st.markdown(f"- **{zone}** → tiri totali: {stats['totali']} | 2PT: {stats['2pt']} | 3PT: {stats['3pt']} | PAT: {stats['pat']}")
    else:
        st.info("Nessun dato ancora per questa sessione.")

# Funzione per aggiungere i tiri per zona
def annotate_zones(ax, player_data):
    # Crea un dizionario con le posizioni per ogni zona
    zone_positions = {
        'Angolo sinistro': (-7.2, 12),     
        'Ala sinistra': (-7, 9),
        'Centro sinistra':(-4, 5.5),
        'Centro': (0, 5.5),
        'Centro destra': (4, 5.5),
        'Ala destra': (7, 9),
        'Angolo destro': (7.2, 12)
    }
    
    # Aggiungi i tiri per ciascuna zona
    for zone, stats in player_data.items():
        if stats["2pt"] > 0:
            ax.text(zone_positions[zone][0], zone_positions[zone][1], f"2PT: {stats['2pt']}", 
                    ha='center', va='center', fontsize=12, color='blue')
        if stats["3pt"] > 0:
            ax.text(zone_positions[zone][0], zone_positions[zone][1] + 0.5, f"3PT: {stats['3pt']}", 
                    ha='center', va='center', fontsize=12, color='green')
        if stats["pat"] > 0:
            ax.text(zone_positions[zone][0], zone_positions[zone][1] - 0.5, f"PAT: {stats['pat']}", 
                    ha='center', va='center', fontsize=12, color='red')

# Funzione per calcolare le statistiche aggregate per sessione
def calculate_aggregated_stats(session_data):
    # Inizializza i totali
    total_2pt = 0
    total_3pt = 0
    total_pat = 0

    # Itera sui dati per sommare i tiri
    for player, zones in session_data.items():
        for zone, stats in zones.items():
            total_2pt += stats['2pt']
            total_3pt += stats['3pt']
            total_pat += stats['pat']

    return total_2pt, total_3pt, total_pat

# Funzione per generare il report con l'immagine personalizzata per ogni giocatore
def generate_report(session_data):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Report della Sessione di Tiri", ln=True, align='C')

    # Aggiungi i grafici per ogni giocatore
    for player, zones in session_data.items():
        pdf.cell(200, 10, txt=f"Giocatore: {player}", ln=True)

        # Creiamo il grafico per il giocatore
        fig, ax = plt.subplots(figsize=(8, 6))  # Ridotto il formato del grafico
        draw_half_court(ax)
        annotate_zones(ax, zones)  # Aggiungi le annotazioni per ogni zona di tiro

        # Salva il grafico come immagine in un oggetto BytesIO
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)

        # Salva l'immagine su un file temporaneo
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_img_file:
            temp_img_file.write(img_buffer.getvalue())
            temp_img_file.close()

            # Aggiungi l'immagine del grafico al PDF
            pdf.image(temp_img_file.name, x=10, y=pdf.get_y(), w=140)  # Ridotto la larghezza dell'immagine

            pdf.ln(80)  # Aggiungi uno spazio tra i grafici dei giocatori

    # Calcola le statistiche aggregate
    total_2pt, total_3pt, total_pat = calculate_aggregated_stats(session_data)

    # Aggiungi le statistiche aggregate in una tabella
    pdf.ln(20)
    pdf.set_font("Arial", size=10)
    pdf.cell(40, 10, "Statistica", border=1, align='C')
    pdf.cell(40, 10, "Totale", border=1, align='C')
    pdf.ln(10)

    pdf.cell(40, 10, "Canestri da 2PT", border=1, align='C')
    pdf.cell(40, 10, str(total_2pt), border=1, align='C')
    pdf.ln(10)

    pdf.cell(40, 10, "Canestri da 3PT", border=1, align='C')
    pdf.cell(40, 10, str(total_3pt), border=1, align='C')
    pdf.ln(10)

    pdf.cell(40, 10, "Canestri da 2PT (PAT)", border=1, align='C')
    pdf.cell(40, 10, str(total_pat), border=1, align='C')
    pdf.ln(10)

    # Salva il PDF su un file temporaneo
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file_path = tmp_file.name
        pdf.output(tmp_file_path)
        return tmp_file_path

# --- Genera il Report ---
if st.session_state.session_data:
    session_key = str(session_date)
    if session_key in st.session_state.session_data:
        st.subheader("📝 Genera il Report PDF")
        report_file = generate_report(st.session_state.session_data[session_key])
        with open(report_file, "rb") as f:
            st.download_button(
                label="Download Report PDF",
                data=f,
                file_name="sessione_tiri_report.pdf",
                mime="application/pdf"
            )