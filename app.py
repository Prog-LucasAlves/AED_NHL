"""
App Streamlit para visualização de dados da NHL.
"""
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="NHL Data Dashboard",
    page_icon="🏒",
    layout="wide",
    initial_sidebar_state="expanded"
)
