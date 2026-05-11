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
    
    # === NEW: Display the Original Matrix ===
    st.subheader("Your Original Zwicky Matrix")
    st.write("This foundational grid contains all the elements used to generate the scenarios below.")
    st.dataframe(st.session_state.matrix, use_container_width=True, hide_index=True)
    st.divider()
    # ========================================

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

        # --- EXPORT TO CSV & PRINT PDF ---
        st.divider()
        st.subheader("Save Your Work")
        
        # 1. Build the CSV Download
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(["# ZWICKY BOX STORY GENERATOR (Classroom Edition)"])
        writer.writerow(["# developed by Keis Ohtsuka (c) 2026 using Google Gemini Pro."])
        writer.writerow([])
        writer.writerow(["# ORIGINAL ZWICKY MATRIX"])
        st.session_state.matrix.to_csv(csv_buffer, index=False)
        writer.writerow([])
        writer.writerow(["# THE 5 CORE SCENARIOS (Without Replacement)"])
        st.session_state.core_df.to_csv(csv_buffer, index=False)
        writer.writerow([])
        writer.writerow([f"# RANDOMLY SAMPLED SCENARIOS - Total: {len(st.session_state.random_cases)}"])
        random_df.to_csv(csv_buffer, index=False)
        
        # 2. Build the HTML Printable Report (Triggers PDF Print Automatically)
        html_report = f"""
        <html><head><title>Zwicky Box Results</title>
        <style>body {{ font-family: sans-serif; padding: 20px; }} table {{ border-collapse: collapse; width: 100%; margin-bottom: 30px; }} th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }} th {{ background-color: #eee; }}</style>
        </head><body onload="window.print()">
        <h2>Zwicky Box Story Generator - Results</h2>
        <p><i>Developed by Keis Ohtsuka (c) 2026</i></p>
        <h3>Original Zwicky Matrix</h3>
        {st.session_state.matrix.to_html(index=False)}
        <h3>Core Scenarios</h3>
        {st.session_state.core_df.to_html(index=False)}
        <h3>Random Scenarios</h3>
        {random_df.to_html(index=False)}
        </body></html>
        """

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📊 Download as CSV Spreadsheet",
                data=csv_buffer.getvalue(),
                file_name="zwicky_results.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col2:
            st.download_button(
                label="🖨️ Download Printable PDF Report",
                data=html_report,
                file_name="Zwicky_Printable_Report.html",
                mime="text/html",
                use_container_width=True,
                help="Clicking this will download a file. Open it, and it will automatically open your computer's Print menu!"
            )
        
    # --- EXIT FLOW ---
    st.divider()
    st.subheader("Are you finished?")
    
    col_n, col_y = st.columns(2)
    with col_n:
        if st.button("🔄 No, Start Over", use_container_width=True):
            st.session_state.clear()
            st.rerun()
            
    with col_y:
        if st.button("✅ Yes, I am done", use_container_width=True):
            st.session_state.show_quit = True
            st.rerun()
            
    # The Quit warning only appears if they say they are done
    if st.session_state.show_quit:
        st.warning("⚠️ **Clicking Quit will permanently erase your current scenarios.** Please make sure you have saved or printed them!")
        if st.button("🚪 Confirm & Quit Application", type="primary"):
            st.session_state.phase = 'quit'
            st.rerun()

# --- PHASE 4: QUIT SCREEN ---
elif st.session_state.phase == 'quit':
    st.session_state.clear() 
    
    st.markdown("<h1 style='text-align: center; color: #2c3e50;'>Goodbye! 👋</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Thank you for using the Zwicky Box Story Generator.</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7f8c8d;'>Your session has ended and your data has been securely cleared. You can now safely close this browser tab.</p>", unsafe_allow_html=True)