import os

import streamlit as st
import streamlit.components.v1 as components

_HTML_PATH = os.path.join(os.path.dirname(__file__), "lung_widget_build", "index.html")


def _load_lung_html(batang: int, lama: int) -> str:
    with open(_HTML_PATH, encoding="utf-8") as f:
        html = f.read()
    return (
        html.replace("__BATANG__", str(int(batang)))
        .replace("__LAMA__", str(int(lama)))
    )


def render_lung_display(batang: int = 0, lama: int = 0):
    components.html(_load_lung_html(batang, lama), height=520, scrolling=False)


def render_lung_widget(batang: int = 0, lama: int = 0, key=None):
    render_lung_display(batang, lama)

    lama_key = f"{key}_lama_slider" if key else "lung_lama_slider"
    batang_key = f"{key}_batang_slider" if key else "lung_batang_slider"

    c1, c2 = st.columns(2)
    with c1:
        lama_out = st.slider("Lama merokok (tahun)", 0, 50, int(lama), key=lama_key)
    with c2:
        batang_out = st.slider("Batang / hari", 0, 30, int(batang), key=batang_key)

    return {"batang": int(batang_out), "lama": int(lama_out)}
