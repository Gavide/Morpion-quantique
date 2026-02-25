import streamlit as st
import streamlit.components.v1 as components

def apply_base():
    bg_url = "https://images.unsplash.com/photo-1614850523296-d8c1af93d400?q=80&w=2070"
    st.markdown(f"""
    <style>
    header,[data-testid="stHeader"],.stAppHeader,
    #MainMenu,footer,[data-testid="stFooter"],
    .viewerBadge_container__r5tak,[class*="viewerBadge"],
    [data-testid="stStatusWidget"],
    h1 a,h2 a,h3 a,.anchor-link {{display:none!important}}

    .stApp {{
        background:linear-gradient(rgba(0,0,0,0.92),rgba(0,0,0,0.92)),
                   url("{bg_url}") center/cover no-repeat fixed;
        color:white;
    }}

    /* Sidebar fond + bouton retour */
    [data-testid="stSidebar"] {{background:#0a0a0a!important}}
    [data-testid="stSidebar"] div.stButton > button {{
        height:40px!important;min-height:40px!important;
        font-size:12px!important;font-weight:700!important;
        padding:0 12px!important;
        background:#0f1c35!important;
        border:1px solid #2a5298!important;
        color:#6fa8dc!important;
        border-radius:6px!important;
        letter-spacing:1px!important;text-transform:uppercase!important;
        box-shadow:none!important;width:100%;
        transition:background 0.2s,border-color 0.2s,color 0.2s!important;
    }}
    [data-testid="stSidebar"] div.stButton > button:hover {{
        background:#162d52!important;
        border-color:#4a90d9!important;
        color:#a8d1f5!important;
    }}

    /* Titre menu */
    .main-header {{
        font-size:130px;font-weight:900;text-align:center;color:white;
        text-shadow:0 0 35px rgba(0,255,255,0.8);
        margin-bottom:140px;line-height:0.9;
        font-family:'Arial Black',sans-serif;
    }}

    /* Historique */
    [data-testid="stTable"] *        {{color:#d0d0d0!important}}
    [data-testid="stTable"] thead th {{color:#fff!important;font-weight:700!important}}
    [data-testid="stTable"] tbody tr:nth-child(even) {{background:rgba(255,255,255,0.04)!important}}

    /* Onglets */
    [data-testid="stTabs"] button[role="tab"] {{
        font-size:20px!important;font-weight:700!important;padding:10px 22px!important;
    }}

    /* Gate sequence fond blanc */
    [data-testid="stCode"] pre {{
        background:#ffffff!important;color:#111!important;
        border:1px solid #ddd!important;border-radius:6px!important;
        font-family:"Courier New",Courier,monospace!important;
    }}
    [data-testid="stCode"] {{background:#ffffff!important;border-radius:6px!important;}}
    </style>
    """, unsafe_allow_html=True)


def apply_game_buttons():
    """Boutons grands VALIDER/RESET + petits boutons grille. À appeler sur les pages de jeu seulement."""
    st.markdown("""
    <style>
    /* Boutons jeu — gris anthracite, neutre, ne confond pas avec couleurs joueurs */
    [data-testid="stMain"] div.stButton > button {
        height:60px!important;
        font-size:18px!important;font-weight:700!important;
        background:#1c1c1c!important;
        border:2px solid #3a3a3a!important;
        color:#c8c8c8!important;
        border-radius:6px!important;
        letter-spacing:2px!important;text-transform:uppercase!important;
        transition:background 0.2s,border-color 0.2s,box-shadow 0.2s,color 0.2s!important;
        box-shadow:none!important;
    }
    [data-testid="stMain"] div.stButton > button:hover {
        background:#2c2c2c!important;
        border-color:#666!important;
        color:#ffffff!important;
        box-shadow:0 0 10px rgba(255,255,255,0.07)!important;
    }
    /* Bouton VALIDER (primary) — violet */
    [data-testid="stMain"] div.stButton > button[kind="primary"] {
        background:#1e0e35!important;
        border:2px solid #7b3fa0!important;
        color:#c084fc!important;
    }
    [data-testid="stMain"] div.stButton > button[kind="primary"]:hover {
        background:#2d1550!important;
        border-color:#a855f7!important;
        color:#e0abff!important;
        box-shadow:0 0 14px rgba(168,85,247,0.35)!important;
    }
    /* Boutons grille coordonnées — minuscules */
    div[data-testid="stHorizontalBlock"] div.stButton > button {
        height:22px!important;min-height:22px!important;
        font-size:10px!important;font-weight:500!important;
        padding:0 4px!important;line-height:1!important;
        background:#1a1a1a!important;
        border:1px solid rgba(255,255,255,0.18)!important;
        color:rgba(210,210,210,0.85)!important;
        border-radius:3px!important;
        letter-spacing:0!important;text-transform:none!important;
        box-shadow:none!important;
        transition:background 0.15s,color 0.15s!important;
    }
    div[data-testid="stHorizontalBlock"] div.stButton > button:hover {
        background:#2a2a2a!important;color:#fff!important;
        border-color:rgba(255,255,255,0.4)!important;
    }
    div[data-testid="stHorizontalBlock"] div.stButton > button:disabled {
        opacity:0.18!important;cursor:default!important;
    }
    </style>
    """, unsafe_allow_html=True)


def apply_menu_button_styles(current_action):
    """JS : gros boutons menu avec letter-spacing hover animé."""
    blue, red = "0,200,255", "255,60,60"
    cfg = {
        "MULTIJOUEUR LOCAL": (blue, "LOCAL"),
        "ORDINATEUR":        (red,  "IA"),
        "INFORMATIONS":      (blue, "INFOS"),
        "PERSONNALISATION":  (red,  "PERSO"),
    }
    js_cfg = "{"
    for txt, (rgb, key) in cfg.items():
        active = str(current_action == key).lower()
        js_cfg += f'"{txt}":{{"rgb":"{rgb}","active":{active}}},'
    js_cfg += "}"

    # Le JS cherche TOUS les boutons du document (pas seulement stMain)
    # car ils sont dans des colonnes imbriquées
    script = f"""<script>
(function(){{
  var cfg={js_cfg};
  function run(){{
    var doc=window.parent.document;
    // Cherche tous les boutons — on filtre par texte
    var all=doc.querySelectorAll('button[kind="secondary"],div.stButton > button');
    all.forEach(function(btn){{
      var txt=(btn.innerText||btn.textContent||'').trim();
      var c=null;
      for(var k in cfg){{if(txt.includes(k)){{c=cfg[k];break;}}}}
      if(!c)return;
      // Skip les boutons sidebar
      if(btn.closest('[data-testid="stSidebar"]'))return;
      var rgb=c.rgb, act=c.active;
      btn.style.setProperty('height','120px','important');
      btn.style.setProperty('font-size','42px','important');
      btn.style.setProperty('font-weight','900','important');
      btn.style.setProperty('border-radius','0','important');
      btn.style.setProperty('letter-spacing','2px','important');
      btn.style.setProperty('text-transform','uppercase','important');
      btn.style.setProperty('color','white','important');
      btn.style.setProperty('width','100%','important');
      btn.style.setProperty('transition',
        'letter-spacing 0.35s ease,box-shadow 0.25s ease,background 0.25s ease,border-color 0.25s ease',
        'important');
      btn.style.setProperty('background',act?'rgba('+rgb+',0.08)':'rgba(255,255,255,0.03)','important');
      btn.style.setProperty('border','2px solid '+(act?'rgba('+rgb+',0.65)':'rgba('+rgb+',0.35)'),'important');
      btn.style.setProperty('box-shadow',act?'0 0 14px rgba('+rgb+',0.45)':'0 0 8px rgba('+rgb+',0.2)','important');
      btn.style.setProperty('text-decoration',act?'line-through':'none','important');
      btn.style.setProperty('text-decoration-thickness',act?'4px':'0','important');
      btn.style.setProperty('text-decoration-color','rgba('+rgb+',0.9)','important');
      // Détacher anciens listeners
      if(btn._hi)btn.removeEventListener('mouseenter',btn._hi);
      if(btn._ho)btn.removeEventListener('mouseleave',btn._ho);
      var cb=act?'rgba('+rgb+',0.65)':'rgba('+rgb+',0.35)';
      var cs=act?'0 0 14px rgba('+rgb+',0.45)':'0 0 8px rgba('+rgb+',0.2)';
      var cg=act?'rgba('+rgb+',0.08)':'rgba(255,255,255,0.03)';
      btn._hi=function(){{
        this.style.setProperty('letter-spacing','6px','important');
        this.style.setProperty('border-color','rgba('+rgb+',0.95)','important');
        this.style.setProperty('box-shadow','0 0 22px rgba('+rgb+',0.75),0 0 45px rgba('+rgb+',0.35)','important');
        this.style.setProperty('background','rgba('+rgb+',0.13)','important');
      }};
      btn._ho=function(){{
        this.style.setProperty('letter-spacing','2px','important');
        this.style.setProperty('border-color',cb,'important');
        this.style.setProperty('box-shadow',cs,'important');
        this.style.setProperty('background',cg,'important');
      }};
      btn.addEventListener('mouseenter',btn._hi);
      btn.addEventListener('mouseleave',btn._ho);
    }});
  }}
  run();setTimeout(run,100);setTimeout(run,400);setTimeout(run,900);
}})();
</script>"""
    components.html(script, height=0)