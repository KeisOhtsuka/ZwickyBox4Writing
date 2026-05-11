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

# --- STATE MANAGEMENT ---
if 'phase' not in st.session_state:
    st.session_state.phase = 'input'  
if 'matrix_data' not in st.session_state:
    st.session_state.matrix_data = [] # Holds the completed rows securely
if 'matrix' not in st.session_state:
    st.session_state.matrix = None # Will hold the final Pandas DataFrame
if 'student_scenario' not in st.session_state:
    st.session_state.student_scenario = []
if 'remaining_columns' not in st.session_state:
    st.session_state.remaining_columns = []
if 'current_col_idx' not in st.session_state:
    st.session_state.current_col_idx = 0
if 'available_items' not in st.session_state:
    st.session_state.available_items = []
if 'rejected_items' not in st.session_state:
    st.session_state.rejected_items = []
if 'current_roll' not in st.session_state:
    st.session_state.current_roll = None

columns_list = ['Character(s)', 'Setting', 'Objects', 'Crisis', 'Action']

# --- PHASE 1: THE ROW-BY-ROW INPUT ---
if st.session_state.phase == 'input':
    st.subheader("1. Build Your Matrix")
    st.write("Fill out your story elements **one row at a time**.")

    # Display the current progress as a safe, read-only table
    display_data = st.session_state.matrix_data + [["", "", "", "", ""] for _ in range(5 - len(st.session_state.matrix_data))]
    st.dataframe(pd.DataFrame(display_data, columns=columns_list), use_container_width=True, hide_index=True)

    # If they haven't finished all 5 rows, show the input form for the current row
    if len(st.session_state.matrix_data) < 5:
        current_row_num = len(st.session_state.matrix_data) + 1
        st.markdown(f"### 📝 Entering Data for Row {current_row_num}")
        
        # We use a form so it doesn't refresh until they click the button
        with st.form(key=f"row_form_{current_row_num}"):
            col1, col2, col3, col4, col5 = st.columns(5)
            val1 = col1.text_input("Character(s)")
            val2 = col2.text_input("Setting")
            val3 = col3.text_input("Objects")
            val4 = col4.text_input("Crisis")
            val5 = col5.text_input("Action")

            submit_btn = st.form_submit_button(f"Save Row {current_row_num}")

            if submit_btn:
                # Ensure they didn't leave any blanks
                if all(v.strip() for v in [val1, val2, val3, val4, val5]):
                    st.session_state.matrix_data.append([val1, val2, val3, val4, val5])
                    st.rerun() # Refresh the page to show the new row
                else:
                    st.error("⚠️ Please fill in all 5 columns before saving.")
                    
    # If all 5 rows are done, lock it in!
    else:
        st.success("Matrix complete! Ready to build your scenario.")
        if st.button("🎲 Lock Matrix & Start Dice Roll!", type="primary"):
            # Convert the safe list data into the final DataFrame for the rest of the app
            st.session_state.matrix = pd.DataFrame(st.session_state.matrix_data, columns=columns_list)
            st.session_state.phase = 'rolling'
            st.rerun()


# --- PHASE 2: THE GAMIFIED DICE ROLL ---
elif st.session_state.phase == 'rolling':
    df = st.session_state.matrix
    columns = df.columns.tolist()
    current_col_name = columns[st.session_state.current_col_idx]

    st.subheader(f"2. Build Your Custom Scenario")
    st.progress((st.session_state.current_col_idx) / 5)
    
    if not st.session_state.available_items and st.session_state.current_roll is None:
        pool = df[current_col_name].tolist()
        random.shuffle(pool)
        st.session_state.available_items = pool
        st.session_state.rejected_items = []

    if st.session_state.current_roll is None:
        if len(st.session_state.available_items) == 1:
            forced_item = st.session_state.available_items.pop(0)
            st.session_state.student_scenario.append(forced_item)
            st.session_state.remaining_columns.append(st.session_state.rejected_items)
            st.warning(f"⚠️ Last option remaining for **{current_col_name}**! Auto-locked: **{forced_item}**")
            
            st.session_state.current_col_idx += 1
            if st.session_state.current_col_idx >= 5:
                st.session_state.phase = 'results'
            st.rerun()
        else:
            st.session_state.current_roll = st.session_state.available_items.pop(0)

    if st.session_state.current_roll is not None:
        st.info(f"### Rolling for: {current_col_name.upper()}")
        st.markdown(f"## 🎲 Rolled: **{st.session_state.current_roll}**")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("✅ Keep This", use_container_width=True, type="primary"):
                st.session_state.student_scenario.append(st.session_state.current_roll)
                leftovers = st.session_state.available_items + st.session_state.rejected_items
                st.session_state.remaining_columns.append(leftovers)
                
                st.session_state.current_col_idx += 1
                st.session_state.current_roll = None
                st.session_state.available_items = [] 
                
                if st.session_state.current_col_idx >= 5:
                    st.session_state.phase = 'results'
                st.rerun()
                
        with col2:
            if st.button("🔄 Roll Again", use_container_width=True):
                st.session_state.rejected_items.append(st.session_state.current_roll)
                st.session_state.current_roll = None
                st.rerun()
                
    st.divider()
    st.write("**Your Story So Far:**")
    st.write(" / ".join(st.session_state.student_scenario) if st.session_state.student_scenario else "(Nothing locked in yet)")


# --- PHASE 3: RESULTS & EXPLORER ---
elif st.session_state.phase == 'results':
    st.success("🎉 YOUR CUSTOM SCENARIO IS COMPLETE!")
    st.markdown(f"### {' / '.join(st.session_state.student_scenario)}")
    st.divider()
    
    columns = st.session_state.matrix.columns.tolist()
    
    if 'core_df' not in st.session_state:
        for col in st.session_state.remaining_columns:
            random.shuffle(col)
            
        other_4_cases = [[st.session_state.remaining_columns[c][r] for c in range(5)] for r in range(4)]
        all_5_cases = [st.session_state.student_scenario] + other_4_cases
        
        st.session_state.core_df = pd.DataFrame(all_5_cases, columns=columns)
        plot_ids = ["⭐ Plot 1 (Custom)"] + [f"Plot {i+2}" for i in range(4)]
        st.session_state.core_df.insert(0, "Plot ID", plot_ids)

    st.subheader("The 5 Core Scenarios (Without Replacement)")
    st.write("Plot 1 is your locked-in scenario. Plots 2-5 were built using the remaining elements from your matrix.")
    
    def highlight_first_row(s):
        return ['background-color: #d4efdf' if s.name == 0 else '' for _ in s]
    
    st.dataframe(st.session_state.core_df.style.apply(highlight_first_row, axis=1), use_container_width=True, hide_index=True)

    # --- INFINITE EXPLORER ---
    st.divider()
    st.subheader("Explore Random Scenarios (With Replacement)")
    
    if 'random_cases' not in st.session_state:
        st.session_state.random_cases = []

    if st.button("✨ Draw 5 Random Scenarios"):
        columns_data = [st.session_state.matrix[col].tolist() for col in columns]
        for _ in range(5):
            random_case = [random.choice(col) for col in columns_data]
            st.session_state.random_cases.append(random_case)
            
    if st.session_state.random_cases:
        random_df = pd.DataFrame(st.session_state.random_cases, columns=columns)
        random_ids = [f"Random Plot {i+1}" for i in range(len(st.session_state.random_cases))]
        random_df.insert(0, "Plot ID", random_ids)
        st.dataframe(random_df, use_container_width=True, hide_index=True)

       # --- EXPORT TO CSV & RESET/QUIT ---
        st.divider()
        st.subheader("Save Your Work")
        
        # Build the CSV buffer (Keep your existing CSV logic here)
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(["# ZWICKY BOX STORY GENERATOR (Classroom Edition)"])
        writer.writerow(["# developed by Keis Ohtsuka (c) 2026 using Google Gemini Pro."])
        writer.writerow(["# Creative Commons Attribution NonCommercial ShareAlike licence: CC BY NC SA 4.0"])
        writer.writerow([])
        writer.writerow(["# ORIGINAL ZWICKY MATRIX"])
        st.session_state.matrix.to_csv(csv_buffer, index=False)
        writer.writerow([])
        writer.writerow(["# THE 5 CORE SCENARIOS (Without Replacement)"])
        st.session_state.core_df.to_csv(csv_buffer, index=False)
        writer.writerow([])
        writer.writerow([f"# RANDOMLY SAMPLED SCENARIOS - Total: {len(st.session_state.random_cases)}"])
        random_df.to_csv(csv_buffer, index=False)
        
        # Button Layout using columns for a cleaner look
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                label="📥 Download Results (CSV)",
                data=csv_buffer.getvalue(),
                file_name="zwicky_matrix_results.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        with col2:
            if st.button("🔄 Start Over", use_container_width=True):
                st.session_state.clear()
                st.rerun()
                
        with col3:
            if st.button("🚪 Quit", type="primary", use_container_width=True):
                st.session_state.phase = 'quit'
                st.rerun()
        )
        
    # Reset button 
    st.divider()
    if st.button("Reset Everything & Start Over"):
        st.session_state.clear()
        st.rerun()
        # --- PHASE 4: QUIT SCREEN ---
    elif st.session_state.phase == 'quit':
        st.session_state.clear() # Wipes the memory clean
    
        st.markdown("<h1 style='text-align: center; color: #2c3e50;'>Goodbye! 👋</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Thank you for using the Zwicky Box Story Generator.</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #7f8c8d;'>Your session has ended and your data has been cleared. You can now safely close this browser tab.</p>", unsafe_allow_html=True)
    st.divider()
    
    # Just in case they clicked it by accident
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Wait, take me back! (Start Over)", use_container_width=True):
            st.rerun()
