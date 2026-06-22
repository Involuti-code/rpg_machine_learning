import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt

# ── Paleta & tema ──────────────────────────────────────────────────────────
BG         = "#0d1117"
PANEL      = "#161b22"
PANEL_ALT  = "#1c2333"
BORDER     = "#30363d"
TEXT       = "#e6edf3"
TEXT_MUTED = "#8b949e"
ACCENT     = "#7c3aed"
ACCENT2    = "#a78bfa"
GOLD       = "#fbbf24"

CLASS_COLORS = {
    "Guerreiro": "#ef4444",
    "Arqueiro":  "#22c55e",
    "Mago":      "#a855f7",
}
CLASS_ICONS = {
    "Guerreiro": "⚔️",
    "Arqueiro":  "🏹",
    "Mago":      "🔮",
}

STAT_META = {
    "forca":        ("Força",        "💪", ACCENT),
    "agilidade":    ("Agilidade",    "🏃", "#06b6d4"),
    "inteligencia": ("Inteligência", "🧠", GOLD),
    "vitalidade":   ("Vitalidade",   "❤️",  "#f43f5e"),
}


def style_figure(fig, ax):
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=TEXT_MUTED, labelsize=10)
    ax.xaxis.label.set_color(TEXT_MUTED)
    ax.yaxis.label.set_color(TEXT_MUTED)
    ax.title.set_color(TEXT)
    ax.title.set_fontsize(13)
    ax.title.set_fontweight("bold")
    for spine in ax.spines.values():
        spine.set_color(BORDER)
    ax.grid(True, color=BORDER, alpha=0.5, linewidth=0.6)


def inject_css(initial_view=False):
    chart_max_h = "310px" if initial_view else "none"
    chart_rule = (
        f"""
        div[data-testid="stPyplotGlobalUseContainerWidthTrue"],
        div[data-testid="stPyplotGlobalUseContainerWidthFalse"] {{
            max-height: {chart_max_h} !important;
        }}
        div[data-testid="stPyplotGlobalUseContainerWidthTrue"] img,
        div[data-testid="stPyplotGlobalUseContainerWidthFalse"] img {{
            max-height: {chart_max_h} !important;
            object-fit: contain !important;
        }}
        """
        if initial_view else ""
    )

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        .block-container {{
            max-width: 1680px;
            padding: {"0.9rem 2rem 0.75rem 2rem" if initial_view else "1.25rem 2.5rem 1.5rem 2.5rem"} !important;
        }}

        section[data-testid="stSidebar"] {{
            background: {PANEL};
            border-right: 1px solid {BORDER};
        }}
        section[data-testid="stSidebar"] .block-container {{
            padding-top: 1.5rem;
        }}
        div[data-testid="stSlider"] label {{
            color: {TEXT} !important;
            font-weight: 600;
            font-size: 0.85rem;
        }}
        div[data-testid="stSidebar"] button {{
            background: linear-gradient(135deg, {ACCENT}, {ACCENT2}) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            letter-spacing: 0.04em !important;
            padding: 0.65rem 1rem !important;
            width: 100% !important;
        }}
        div[data-testid="stSidebar"] button:hover {{
            opacity: 0.88 !important;
        }}

        .hero {{
            background: linear-gradient(135deg, {PANEL} 0%, {PANEL_ALT} 100%);
            border: 1px solid {BORDER};
            border-radius: 16px;
            padding: {"1.25rem 1.75rem" if initial_view else "1.75rem 2rem"};
            margin-bottom: {"1rem" if initial_view else "1.5rem"};
        }}
        .hero h1 {{
            margin: 0 0 0.4rem 0;
            font-size: 1.75rem;
            font-weight: 700;
            color: {TEXT};
            letter-spacing: -0.02em;
        }}
        .hero p {{
            margin: 0;
            color: {TEXT_MUTED};
            font-size: 0.95rem;
            line-height: 1.5;
        }}
        .hero-tags {{
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }}
        .tag {{
            background: {PANEL_ALT};
            border: 1px solid {BORDER};
            border-radius: 20px;
            padding: 0.25rem 0.75rem;
            font-size: 0.78rem;
            color: {TEXT_MUTED};
            font-weight: 500;
        }}

        .stat-card {{
            background: {PANEL};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 1rem 1.1rem;
            text-align: center;
        }}
        .stat-icon {{ font-size: 1.4rem; margin-bottom: 0.3rem; }}
        .stat-label {{
            color: {TEXT_MUTED};
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }}
        .stat-value {{
            color: {TEXT};
            font-size: 1.6rem;
            font-weight: 700;
            margin-top: 0.15rem;
        }}
        .stat-bar-bg {{
            background: {BORDER};
            border-radius: 4px;
            height: 4px;
            margin-top: 0.6rem;
            overflow: hidden;
        }}
        .stat-bar-fill {{ height: 100%; border-radius: 4px; }}

        .result-card {{
            background: linear-gradient(135deg, {PANEL_ALT} 0%, {PANEL} 100%);
            border: 1px solid {ACCENT};
            border-radius: 16px;
            padding: 1.75rem 2rem;
            text-align: center;
            box-shadow: 0 0 30px rgba(124, 58, 237, 0.15);
        }}
        .result-label {{
            color: {TEXT_MUTED};
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}
        .result-class {{
            font-size: 2.4rem;
            font-weight: 800;
            color: {TEXT};
            margin: 0.4rem 0 0.2rem;
            letter-spacing: -0.02em;
        }}
        .result-icon {{ font-size: 3rem; margin-bottom: 0.5rem; }}

        .prob-row {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.65rem;
        }}
        .prob-label {{
            width: 90px;
            font-size: 0.82rem;
            font-weight: 600;
            color: {TEXT};
            flex-shrink: 0;
        }}
        .prob-track {{
            flex: 1;
            background: {BORDER};
            border-radius: 6px;
            height: 10px;
            overflow: hidden;
        }}
        .prob-fill {{ height: 100%; border-radius: 6px; }}
        .prob-pct {{
            width: 44px;
            text-align: right;
            font-size: 0.82rem;
            font-weight: 700;
            color: {TEXT_MUTED};
            flex-shrink: 0;
        }}

        .section-title {{
            color: {TEXT};
            font-size: 1.05rem;
            font-weight: 700;
            margin: 0 0 0.25rem 0;
            letter-spacing: -0.01em;
        }}
        .section-sub {{
            color: {TEXT_MUTED};
            font-size: 0.85rem;
            margin: 0 0 {"0.65rem" if initial_view else "1rem"} 0;
        }}

        .panel {{
            background: {PANEL};
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 2.5rem 1.5rem;
            text-align: center;
        }}

        {chart_rule}

        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        header[data-testid="stHeader"] {{ background: transparent; }}
    </style>
    """, unsafe_allow_html=True)


def stat_card_html(key, value, max_val=10):
    label, icon, color = STAT_META[key]
    pct = int(value / max_val * 100)
    return f"""
    <div class="stat-card">
        <div class="stat-icon">{icon}</div>
        <div class="stat-label">{label}</div>
        <div class="stat-value">{value}</div>
        <div class="stat-bar-bg">
            <div class="stat-bar-fill" style="width:{pct}%; background:{color};"></div>
        </div>
    </div>
    """


def prob_rows_html(classes, probabilities):
    rows = ""
    for cls, prob in zip(classes, probabilities):
        color = CLASS_COLORS.get(cls, ACCENT)
        pct = prob * 100
        rows += f"""
        <div class="prob-row">
            <div class="prob-label">{cls}</div>
            <div class="prob-track">
                <div class="prob-fill" style="width:{pct:.1f}%; background:{color};"></div>
            </div>
            <div class="prob-pct">{pct:.0f}%</div>
        </div>
        """
    return rows


def plot_probability_bar(classes, probabilities):
    colors = [CLASS_COLORS.get(c, ACCENT) for c in classes]
    fig, ax = plt.subplots(figsize=(7, 3.2))
    bars = ax.barh(classes, probabilities, color=colors, height=0.55, zorder=3)
    for bar, prob in zip(bars, probabilities):
        if prob > 0.05:
            ax.text(
                prob - 0.02, bar.get_y() + bar.get_height() / 2,
                f"{prob:.0%}", va="center", ha="right",
                color="white", fontsize=11, fontweight="bold",
            )
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("Probabilidade", labelpad=8)
    ax.set_title("Probabilidade por Classe", pad=12)
    style_figure(fig, ax)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
    plt.tight_layout(pad=1.2)
    return fig


def plot_scatter(df, compact=False):
    h = 4.0 if compact else 5.0
    fig, ax = plt.subplots(figsize=(7.5, h))
    for cls in df["classe"].unique():
        subset = df[df["classe"] == cls]
        ax.scatter(
            subset["forca"], subset["agilidade"],
            c=CLASS_COLORS.get(cls, ACCENT),
            label=cls, alpha=0.75, s=55,
            edgecolors="white", linewidths=0.4, zorder=3,
        )
    ax.set_xlabel("Força")
    ax.set_ylabel("Agilidade")
    ax.set_title("Força × Agilidade", pad=12)
    ax.legend(
        frameon=True, facecolor=PANEL, edgecolor=BORDER,
        labelcolor=TEXT, fontsize=9,
    )
    style_figure(fig, ax)
    plt.tight_layout(pad=1.2)
    return fig


def plot_intelligence(df, compact=False):
    h = 4.0 if compact else 5.0
    fig, ax = plt.subplots(figsize=(7.5, h))
    for cls in df["classe"].unique():
        subset = df[df["classe"] == cls]
        color = CLASS_COLORS.get(cls, ACCENT)
        ax.hist(
            subset["inteligencia"], bins=10, alpha=0.55,
            color=color, label=cls, edgecolor=BORDER, linewidth=0.8,
        )
    ax.set_xlabel("Inteligência")
    ax.set_ylabel("Frequência")
    ax.set_title("Distribuição da Inteligência", pad=12)
    ax.legend(
        frameon=True, facecolor=PANEL, edgecolor=BORDER,
        labelcolor=TEXT, fontsize=9,
    )
    style_figure(fig, ax)
    plt.tight_layout(pad=1.2)
    return fig


@st.cache_resource
def load_model_assets():
    try:
        model = joblib.load("rpg_classifier.pkl")
        features = joblib.load("model_features.pkl")
        classes = joblib.load("model_classes.pkl")
        return model, features, classes
    except FileNotFoundError:
        st.error(
            "Arquivos do modelo não encontrados.\n"
            "Execute train_model.py primeiro."
        )
        st.stop()


st.set_page_config(
    page_title="RPG Classifier",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

model, model_features, model_classes = load_model_assets()

# ── Sidebar (antes do CSS para saber se é tela inicial) ─────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding-bottom:1.5rem;">
        <div style="font-size:2.2rem;">⚔️</div>
        <div style="color:{TEXT}; font-weight:700; font-size:1.05rem; margin-top:0.3rem;">
            Personagem
        </div>
        <div style="color:{TEXT_MUTED}; font-size:0.78rem;">Ajuste os atributos</div>
    </div>
    """, unsafe_allow_html=True)

    forca = st.slider("Força", 1, 10, 5)
    agilidade = st.slider("Agilidade", 1, 10, 5)
    inteligencia = st.slider("Inteligência", 1, 10, 5)
    vitalidade = st.slider("Vitalidade", 1, 10, 5)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    classify_clicked = st.button("⚡  Classificar Personagem", use_container_width=True)

inject_css(initial_view=not classify_clicked)

user_input_df = pd.DataFrame(
    [[forca, agilidade, inteligencia, vitalidade]],
    columns=model_features,
)

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🎮 Classificador de Classes RPG</h1>
    <p>
        Machine Learning aplicado ao universo RPG — informe os atributos do personagem
        e descubra se ele é Guerreiro, Arqueiro ou Mago.
    </p>
    <div class="hero-tags">
        <span class="tag">⚔️ Guerreiro</span>
        <span class="tag">🏹 Arqueiro</span>
        <span class="tag">🔮 Mago</span>
        <span class="tag">🤖 Regressão Logística</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Stats + resultado ────────────────────────────────────────────────────────
col_stats, col_result = st.columns([3, 2], gap="large")

with col_stats:
    st.markdown('<p class="section-title">Atributos do Personagem</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-sub">Valores selecionados nos controles laterais</p>',
        unsafe_allow_html=True,
    )
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.markdown(stat_card_html("forca", forca), unsafe_allow_html=True)
    with sc2:
        st.markdown(stat_card_html("agilidade", agilidade), unsafe_allow_html=True)
    with sc3:
        st.markdown(stat_card_html("inteligencia", inteligencia), unsafe_allow_html=True)
    with sc4:
        st.markdown(stat_card_html("vitalidade", vitalidade), unsafe_allow_html=True)

with col_result:
    if classify_clicked:
        st.markdown('<p class="section-title">Resultado</p>', unsafe_allow_html=True)
        try:
            prediction = model.predict(user_input_df)
            prediction_proba = model.predict_proba(user_input_df)
            predicted_class = prediction[0]
            icon = CLASS_ICONS.get(predicted_class, "🎮")
            color = CLASS_COLORS.get(predicted_class, ACCENT)

            st.markdown(f"""
            <div class="result-card">
                <div class="result-icon">{icon}</div>
                <div class="result-label">Classe Prevista</div>
                <div class="result-class" style="color:{color};">{predicted_class}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
            st.markdown(
                prob_rows_html(model_classes, prediction_proba[0]),
                unsafe_allow_html=True,
            )
        except Exception as e:
            st.error(f"Erro na previsão: {e}")
    else:
        st.markdown('<p class="section-title">Resultado</p>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="panel">
            <div style="font-size:2.5rem; margin-bottom:0.5rem; opacity:0.4;">🎯</div>
            <div style="color:{TEXT_MUTED}; font-size:0.9rem;">
                Ajuste os atributos e clique em<br><strong>Classificar Personagem</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Gráfico de probabilidades (após classificar — pode rolar) ─────────────────
if classify_clicked:
    try:
        prediction_proba = model.predict_proba(user_input_df)
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.markdown(
            '<p class="section-title">Gráfico de Probabilidades</p>',
            unsafe_allow_html=True,
        )
        fig_prob = plot_probability_bar(model_classes, prediction_proba[0])
        st.pyplot(fig_prob, use_container_width=True)
        plt.close(fig_prob)
    except Exception:
        pass

# ── Contexto dos dados ───────────────────────────────────────────────────────
st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
st.markdown(
    '<p class="section-title">Contexto dos Dados RPG</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="section-sub">Visualizações do conjunto utilizado para treinar a IA</p>',
    unsafe_allow_html=True,
)

try:
    original_df = pd.read_csv("personagens_rpg.csv")
    chart_left, chart_right = st.columns(2, gap="large")
    compact_charts = not classify_clicked

    with chart_left:
        fig_scatter = plot_scatter(original_df, compact=compact_charts)
        st.pyplot(fig_scatter, use_container_width=True)
        plt.close(fig_scatter)

    with chart_right:
        fig_hist = plot_intelligence(original_df, compact=compact_charts)
        st.pyplot(fig_hist, use_container_width=True)
        plt.close(fig_hist)

except Exception as e:
    st.warning(f"Erro ao carregar visualizações: {e}")
