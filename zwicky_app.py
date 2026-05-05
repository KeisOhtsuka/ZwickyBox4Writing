import streamlit as st
import pandas as pd
import random
import csv
from io import StringIO

# --- SETUP & CREDITS ---
st.set_page_config(page_title="Zwicky Box Story Generator", page_icon="🎲", layout="wide")

st.title("🎲 Zwicky Box Story Generator")
st.markdown("**Developed by Keis Ohtsuka (c) 2026 using Google Gemini Pro.**")
st.markdown("*Creative Commons Attribution NonCommercial ShareAlike licence: CC BY NC SA 4.0*")
st.divider()

# --- 1. THE MATRIX INPUT ---
st.subheader("1. Build Your Matrix")
st.write("Fill out the 5x5 grid below with your story elements.")

# Create an empty dataframe for the students to type into
if 'matrix' not in st.session_state:
    st.session_state.matrix = pd.DataFrame(
        [["", "", "", "", ""] for _ in range(5)],
        columns=['Character(s)', 'Setting', 'Objects', 'Crisis', 'Action']
    )

# st.data_editor creates a beautiful Excel-like grid right on the webpage
edited_df = st.data_editor(st.session_state.matrix, use_container_width=True, hide_index=True)

# Check if the matrix is fully filled out
is_filled = not edited_df.replace("", pd.NA).isna().values.any()

if is_filled:
    st.success("Matrix complete! Let's generate some stories.")
    
    # --- 2. CORE SCENARIOS (Without Replacement) ---
    st.subheader("2. The 5 Core Scenarios")
    st.write("These 5 scenarios use every element from your matrix exactly once, with no overlaps.")
    
    if st.button("🎲 Shuffle & Generate Core Scenarios"):
        # Convert columns to lists and shuffle them
        columns_data = [edited_df[col].tolist() for col in edited_df.columns]
        for col in columns_data:
            random.shuffle(col)
            
        # Reassemble into 5 rows
        core_cases = [[columns_data[c][r] for c in range(5)] for r in range(5)]
        
        # Save to session state so it doesn't disappear when they click other buttons
        st.session_state.core_df = pd.DataFrame(core_cases, columns=edited_df.columns)
        st.session_state.core_df.insert(0, "Plot ID", [f"Core Plot {i+1}" for i in range(5)])

    if 'core_df' in st.session_state:
        # Display the results as a clean, styled web table
        st.dataframe(st.session_state.core_df, use_container_width=True, hide_index=True)

    # --- 3. INFINITE EXPLORER (With Replacement) ---
    st.divider()
    st.subheader("3. Explore Random Scenarios")
    st.write("Click the button below to draw random combinations. You can keep clicking to add more!")
    
    if 'random_cases' not in st.session_state:
        st.session_state.random_cases = []

    if st.button("✨ Draw 5 Random Scenarios"):
        columns_data = [edited_df[col].tolist() for col in edited_df.columns]
        for _ in range(5):
            random_case = [random.choice(col) for col in columns_data]
            st.session_state.random_cases.append(random_case)
            
    if st.session_state.random_cases:
        random_df = pd.DataFrame(st.session_state.random_cases, columns=edited_df.columns)
        # Add ID tags
        plot_ids = [f"Random Plot {i+1}" for i in range(len(st.session_state.random_cases))]
        random_df.insert(0, "Plot ID", plot_ids)
        
        st.dataframe(random_df, use_container_width=True, hide_index=True)

        # --- 4. EXPORT TO CSV ---
        st.divider()
        st.subheader("4. Save Your Work")
        st.write("Download all your generated scenarios as a spreadsheet.")
        
        # Build the CSV string in memory
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)
        
        writer.writerow(["# ZWICKY BOX STORY GENERATOR (Classroom Edition)"])
        writer.writerow(["# developed by Keis Ohtsuka (c) 2026 using Google Gemini Pro."])
        writer.writerow(["# Creative Commons Attribution NonCommercial ShareAlike licence: CC BY NC SA 4.0"])
        writer.writerow([])
        writer.writerow(["# ORIGINAL ZWICKY MATRIX"])
        edited_df.to_csv(csv_buffer, index=False)
        
        if 'core_df' in st.session_state:
            writer.writerow([])
            writer.writerow(["# THE 5 CORE SCENARIOS (Without Replacement)"])
            st.session_state.core_df.to_csv(csv_buffer, index=False)
            
        writer.writerow([])
        writer.writerow([f"# RANDOMLY SAMPLED SCENARIOS - Total: {len(st.session_state.random_cases)}"])
        random_df.to_csv(csv_buffer, index=False)
        
        # Streamlit's native download button!
        st.download_button(
            label="📥 Download CSV File",
            data=csv_buffer.getvalue(),
            file_name="zwicky_matrix_results.csv",
            mime="text/csv"
        )