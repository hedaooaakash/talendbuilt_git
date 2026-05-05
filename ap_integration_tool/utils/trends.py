import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def plot_trends(data, cols):
    for col in cols:
        plt.figure(figsize=(10,6))
        sns.lineplot(x=data.index, y=data[col])
        plt.title(f"Trend for {col}")
        st.pyplot()