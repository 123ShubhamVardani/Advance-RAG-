"""ui_theme.py
JARVIS-inspired UI theme for A.K.A.S.H.A.
Dark, modern, with holographic effects and a spinning central sphere.
"""
import streamlit as st

# JARVIS-inspired color palette
THEME_COLORS = {
    "primary": "#00D9FF",      # Cyan (JARVIS blue)
    "secondary": "#FFB703",    # Gold accent
    "dark_bg": "#0A0E27",      # Deep navy
    "darker_bg": "#050810",    # Almost black
    "accent": "#00D9FF",       # Bright cyan
    "text_primary": "#FFFFFF", # White
    "text_secondary": "#B0B8C8" # Light gray
}


def apply_jarvis_theme():
    """Apply JARVIS-inspired custom CSS to Streamlit."""
    st.markdown(f"""
    <style>
        /* Overall page theme */
        .main {{
            background: linear-gradient(135deg, {THEME_COLORS['darker_bg']} 0%, {THEME_COLORS['dark_bg']} 100%);
            color: {THEME_COLORS['text_primary']};
        }}
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {THEME_COLORS['dark_bg']} 0%, {THEME_COLORS['darker_bg']} 100%);
            border-right: 2px solid {THEME_COLORS['primary']};
        }}
        
        /* Main container */
        .main .block-container {{
            max-width: 1200px;
            padding: 2rem;
        }}
        
        /* Chat message styling */
        .chat-message {{
            padding: 1rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            border-left: 4px solid {THEME_COLORS['primary']};
            background: rgba(0, 217, 255, 0.05);
        }}
        
        .chat-message.user {{
            border-left-color: {THEME_COLORS['secondary']};
            background: rgba(255, 183, 3, 0.05);
        }}
        
        /* Buttons */
        .stButton > button {{
            background: linear-gradient(135deg, {THEME_COLORS['primary']} 0%, {THEME_COLORS['accent']} 100%);
            color: {THEME_COLORS['dark_bg']};
            border: none;
            border-radius: 8px;
            font-weight: bold;
            padding: 0.75rem 1.5rem;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            box-shadow: 0 0 20px {THEME_COLORS['primary']};
            transform: translateY(-2px);
        }}
        
        /* Input boxes */
        .stTextInput input, .stTextArea textarea {{
            background: rgba(0, 217, 255, 0.1) !important;
            border: 1px solid {THEME_COLORS['primary']} !important;
            color: {THEME_COLORS['text_primary']} !important;
            border-radius: 8px;
        }}
        
        .stTextInput input::placeholder {{
            color: {THEME_COLORS['text_secondary']};
        }}
        
        /* Headers */
        h1, h2, h3 {{
            color: {THEME_COLORS['primary']};
            text-shadow: 0 0 10px {THEME_COLORS['primary']};
        }}
        
        /* Selectbox */
        .stSelectbox {{
            color: {THEME_COLORS['text_primary']};
        }}
        
        /* Slider */
        .stSlider > div > div > div {{
            background: {THEME_COLORS['primary']};
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            border-bottom: 2px solid {THEME_COLORS['primary']};
        }}
        
        .stTabs [aria-selected="true"] {{
            color: {THEME_COLORS['primary']};
            border-bottom: 3px solid {THEME_COLORS['primary']};
        }}
        
        /* Cards/containers */
        .stContainer {{
            background: rgba(0, 217, 255, 0.02);
            border: 1px solid {THEME_COLORS['primary']};
            border-radius: 12px;
            padding: 1.5rem;
        }}
        
        /* Metrics */
        [data-testid="metric-container"] {{
            background: linear-gradient(135deg, rgba(0, 217, 255, 0.1), rgba(255, 183, 3, 0.05));
            border: 1px solid {THEME_COLORS['primary']};
            border-radius: 8px;
            padding: 1rem;
        }}
        
        /* Spinning sphere animation */
        @keyframes spin {{
            from {{ transform: rotateY(0deg) rotateZ(0deg); }}
            to {{ transform: rotateY(360deg) rotateZ(360deg); }}
        }}
        
        .akasha-sphere {{
            width: 200px;
            height: 200px;
            margin: 2rem auto;
            background: radial-gradient(circle at 30% 30%, {THEME_COLORS['primary']}, {THEME_COLORS['accent']});
            border-radius: 50%;
            box-shadow: 
                0 0 30px {THEME_COLORS['primary']},
                0 0 60px rgba(0, 217, 255, 0.5),
                inset -2px -2px 10px rgba(0, 0, 0, 0.5);
            animation: spin 8s linear infinite;
            position: relative;
        }}
        
        .akasha-sphere::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: radial-gradient(circle at 70% 70%, rgba(255, 255, 255, 0.3), transparent);
            animation: spin 4s linear infinite reverse;
        }}
        
        /* Status indicators */
        .status-online {{
            color: {THEME_COLORS['primary']};
            text-shadow: 0 0 10px {THEME_COLORS['primary']};
            font-weight: bold;
        }}
        
        .status-offline {{
            color: #FF6B6B;
            font-weight: bold;
        }}
        
        /* Warning/Error boxes */
        .stAlert {{
            background: rgba(0, 217, 255, 0.1);
            border: 1px solid {THEME_COLORS['primary']};
            border-radius: 8px;
        }}
    </style>
    """, unsafe_allow_html=True)


def render_central_sphere():
    """Render the spinning JARVIS sphere in the center of the chat area."""
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; margin: 2rem 0;">
        <div class="akasha-sphere"></div>
    </div>
    <div style="text-align: center; color: #00D9FF; font-size: 18px; margin-top: 1rem;">
        <p>🤖 A.K.A.S.H.A. - Advanced Quantum & Agentic System for High-level Analysis</p>
        <p style="color: #B0B8C8; font-size: 14px;">Ready to assist. Awaiting input...</p>
    </div>
    """, unsafe_allow_html=True)


def render_loading_animation():
    """Render a pulsing animation while thinking."""
    st.markdown(f"""
    <style>
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        .thinking {{
            display: inline-block;
            animation: pulse 1.5s infinite;
            color: {THEME_COLORS['primary']};
        }}
    </style>
    <div style="text-align: center; margin: 1rem;">
        <div class="thinking">⚡ A.K.A.S.H.A. is processing... ⚡</div>
    </div>
    """, unsafe_allow_html=True)


__all__ = ["apply_jarvis_theme", "render_central_sphere", "render_loading_animation", "THEME_COLORS"]
