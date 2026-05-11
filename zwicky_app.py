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
    st.session_state.matrix_data = [] 
if 'matrix' not in st.session_state:
    st.session_state.matrix = None 
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
if 'show_quit' not in st.session_state:
    st.session_state.show_quit = False

columns_list = ['Character(s)', 'Setting', 'Objects', 'Crisis', 'Action']

# --- PHASE 1: THE ROW-BY-ROW INPUT (TOP-DOWN LAYOUT) ---
if st.session_state.phase == 'input':
    st.subheader("1. Build Your Matrix")
    st.write("Type your story elements into the boxes below. They will appear in the table once you save the row.")

    if len(st.session_state.matrix_data) < 5:
        current_row_num = len(st.session_state.matrix_data) + 1
        st.markdown(f"<h3 style='color: #0d47a1;'>📝 Entering Data for Row {current_row_num}</h3>", unsafe_allow_html=True)
        
        with st.form(key=f"row_form_{current_row_num}"):
            col1, col2, col3, col4, col5 = st.columns(5)
            val1 = col1.text_input("Character(s)")
            val2 = col2.text_input("Setting")
            val3 = col3.text_input("Objects")
            val4 = col4.text_input("Crisis")
            val5 = col5.text_input("Action")

            submit_btn = st.form_submit_button(f"Save Row {current_row_num}")

            if submit_btn:
                if all(v.strip() for v in [val1, val2, val3, val4, val5]):
                    st.session_state.matrix_data.append([val1, val2, val3, val4, val5])
                    st.rerun() 
                else:
                    st.error("⚠️ Please fill in all 5 columns before saving.")
                    
    else:
        st.success("Matrix complete! Ready to build your scenario.")
        if st.button("🎲 Lock Matrix & Start Dice Roll!", type="primary", use_container_width=True):
            st.session_state.matrix = pd.DataFrame(st.session_state.matrix_data, columns=columns_list)
            st.session_state.phase = 'rolling'
            st.rerun()

    st.markdown("### 📊 Matrix Preview")
    display_data = st.session_state.matrix_data + [["", "", "", "", ""] for _ in range(5 - len(st.session_state.matrix_data))]
    
    df_display = pd.DataFrame(display_data, columns=columns_list)
    def highlight_filled(s):
        return ['background-color: #f8f9fa' if v == "" else 'background-color: #d4efdf' for v in s]
    
    st.dataframe(df_display.style.apply(highlight_filled, axis=1), use_container_width=True, hide_index=True)


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
        st.session_state.current_roll = st.session_state.available_items.pop(0)

    # Check if this is the final item in the bag
    is_last_item = (len(st.session_state.available_items) == 0)

    st.info(f"### Rolling for: {current_col_name.upper()}")
    st.markdown(f"## 🎲 Rolled: **{st.session_state.current_roll}**")
    
    if is_last_item:
        st.warning("⚠️ **Last Option Remaining!** You have rejected all other options, so you must keep this item.")
        if st.button("✅ Acknowledge & Continue", use_container_width=True, type="primary"):
            st.session_state.student_scenario.append(st.session_state.current_roll)
            leftovers = st.session_state.available_items + st.session_state.rejected_items
            st.session_state.remaining_columns.append(leftovers)
            
            st.session_state.current_col_idx += 1
            st.session_state.current_roll = None
            st.session_state.available_items = [] 
            
            if st.session_state.current_col_idx >= 5:
                st.session_state.phase = 'results'
            st.rerun()
    else:
        col1, col2 = st.columns(2)
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

        # --- EXPORT TO CSV & SEQUENTIAL EXIT SCREEN ---
        st.divider()
        st.subheader("Save Your Work")
        st.write("Download your results as a CSV spreadsheet, or press **Ctrl+P** (Windows) / **Cmd+P** (Mac) on your keyboard to instantly print this page as a clean PDF.")
        
        # Build the CSV buffer
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
        
        st.download_button(
            label="📥 Download Results (CSV)",
            data=csv_buffer.getvalue(),
            file_name="zwicky_matrix_results.csv",
            mime="text/csv"
        )
        
    st.divider()
    st.subheader("What's Next?")
    st.write("Would you like to build a brand new matrix from scratch?")
    
    col_y, col_n = st.columns(2)
    with col_y:
        if st.button("🔄 Yes, Start Over", use_container_width=True):
            st.session_state.clear()
            st.rerun()
            
    with col_n:
        if st.button("🛑 No, I am finished", use_container_width=True):
            st.session_state.show_quit = True
            st.rerun()
            
    # The Quit warning only appears if they click "No"
    if st.session_state.show_quit:
        st.warning("⚠️ **Warning:** If you quit, all your current scenarios will be permanently erased.")
        if st.button("🚪 Quit Application", type="primary"):
            st.session_state.phase = 'quit'
            st.rerun()

# --- PHASE 4: QUIT SCREEN ---
elif st.session_state.phase == 'quit':
    st.session_state.clear() 
    
    st.markdown("<h1 style='text-align: center; color: #2c3e50;'>Goodbye! 👋</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Thank you for using the Zwicky Box Story Generator.</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7f8c8d;'>Your session has ended and your data has been securely cleared. You can now safely close this browser tab.</p>", unsafe_allow_html=True)
    st.divider()
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Wait, take me back! (Start Over)", use_container_width=True):
            st.rerun()