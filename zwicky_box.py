import csv
import os
import random
import webbrowser

# Zwicky Box Story Generator (Classroom Edition)
# This script allows students to create a Zwicky Box matrix, lock in a custom scenario through a gamified dice roll mechanic, and explore additional random scenarios.
# The results can be saved to both CSV and HTML formats, with the HTML file designed for easy printing.
# written by Keis Ohtsuka using Google Gemini Pro (2024-06-17) and Python 3.14.
# Ver 1.2
# Key Features: Column-based input, gamified scenario selection, random scenario generation, dynamic file saving with auto-naming, and HTML output with print optimization.
# Instructions: Run the script, input your data for each column,lock in your custom scenario through the dice roll mechanic, explore random scenarios, and choose whether to save your results 
# to a file. The HTML output will automatically open in your web browser for review and printing.
# Note: The script is designed to be user-friendly and interactive, making it suitable for classroom use. It includes input validation and dynamic file naming to prevent overwriting existing files.   
# For best results, ensure you have a modern web browser installed to view the HTML output. The script is compatible with Python 3.14 and may require adjustments for earlier versions.
# Example Usage: Type in character names, settings, objects, crises, and actions when prompted. After entering 5 rows of data, lock in your custom scenario by choosing which rolled item to keep for each column. Then explore additional random scenarios and decide if you want to save your results to a file.
# This script is intended for educational and creative use, encouraging students to think critically about story elements and how they can be combined in unique ways. The gamified selection process adds an element of fun and unpredictability to the scenario creation process.
# Developed with the support of Google Gemini Pro, this script also demonstrates how AI can assist in creating engaging educational tools that foster creativity and critical thinking skills in students. Enjoy crafting your stories with the Zwicky Box Story Generator!
# Note: This script is provided as-is and may require adjustments based on specific classroom needs or Python environment configurations. Always test the script in your environment before using it in a classroom setting.
# Licenses: Creative Commons Attribution Non-Commercial Use ShareAlike 4.0 International License (CC BY NC-SA 4.0)
# (c) Keis Ohtsuka 2026
# For any questions or issues, please contact the developer, Keis.Ohtsuka@gmail.com, or refer to the documentation for Python 3.14 and the Google Gemini Pro API.

def main():
    columns = ['Character(s)', 'Setting', 'Objects', 'Crisis', 'Action']
    col_letters = ['A', 'B', 'C', 'D', 'E']
    data = []
    row_count = 0

    # --- UPDATED CONSOLE HEADER ---
    print("="*80)
    print("ZWICKY BOX STORY GENERATOR (Classroom Edition)")
    print("developed by Keis Ohtsuka (c) 2026 using Google Gemini Pro.")
    print("Creative Commons Attribution NonCommercial ShareAlike licence: CC BY NC SA 4.0")
    print("="*80)
    print("\nPlease enter 5 rows of data for your matrix.")

    # 1. Main input loop
    while True:
        row_count += 1
        print(f"\n--- Row {row_count} ---")
        current_row = []
        
        for col in columns:
            entry = input(f"{col}: ")
            current_row.append(entry)
            
        data.append(current_row)

        if row_count >= 5:
            while True:
                complete = input("\nIs entry completed? (Y/N): ").strip().upper()
                if complete in ['Y', 'N']:
                    break
                print("Invalid input. Please enter 'Y' or 'N'.")
            
            if complete == 'Y':
                break
            else:
                print("\nContinuing to row", row_count + 1, "...")

    # Format the data to include Keycodes
    formatted_data = []
    for r_idx, row in enumerate(data):
        formatted_row = []
        for c_idx, item in enumerate(row):
            keycode = f"{col_letters[c_idx]}{r_idx + 1}"
            formatted_row.append(f"[{keycode}] {item}")
        formatted_data.append(formatted_row)

    # Transpose data into columns for easy picking
    columns_data = [[formatted_data[row_idx][col_idx] for row_idx in range(len(formatted_data))] for col_idx in range(5)]

    # --- Phase 2 - The Gamified Dice Roll (Lock-in Mechanic) ---
    print("\n" + "="*80)
    print("THE DICE ROLL: BUILD YOUR CUSTOM SCENARIO!")
    print("="*80)
    print("Let's lock in your core scenario. You can keep a drawn item or roll again.")
    
    student_scenario = []
    remaining_columns = [] 
    
    for i, col_name in enumerate(columns):
        print(f"\n-- Rolling for {col_name.upper()} --")
        pool = list(columns_data[i])
        random.shuffle(pool)
        rejected = []
        
        while pool:
            item = pool.pop(0)
            
            if not pool:
                print(f"🎲 Last option remaining! Auto-locking: {item}")
                student_scenario.append(item)
                remaining_columns.append(rejected) 
                break
            
            while True:
                choice = input(f"🎲 Rolled: {item} | Keep this? (Y/N): ").strip().upper()
                if choice in ['Y', 'N']:
                    break
                print("Please enter Y or N.")
                
            if choice == 'Y':
                student_scenario.append(item)
                remaining_columns.append(pool + rejected) 
                print(f"✅ Locked in: {item}")
                break
            else:
                rejected.append(item)

    print("\n🎉 YOUR CUSTOM SCENARIO IS COMPLETE!")
    print(" / ".join(student_scenario))

    # Generate the other 4 mutually exclusive scenarios from the leftovers
    for col in remaining_columns:
        random.shuffle(col)
    
    other_4_cases = [[remaining_columns[col_idx][row_idx] for col_idx in range(5)] for row_idx in range(4)]
    base_5_cases = [student_scenario] + other_4_cases

    # --- Phase 3: The Infinite Explorer (With Replacement) ---
    print("\n" + "="*80)
    print("EXPLORING RANDOM SCENARIOS (With Replacement)")
    print("="*80)
    
    viewed_cases = []
    case_counter = 0
    
    while True:
        for _ in range(20):
            case_counter += 1
            random_case = [random.choice(col) for col in columns_data]
            viewed_cases.append(random_case)
            print(f"Plot {case_counter:04d} | {' / '.join(random_case)}")
            
        more = input(f"\nShowing {case_counter} random cases. Do you want to see 20 more? (Y/N): ").strip().upper()
        if more == 'N':
            break

    # --- Phase 4: Dynamic Save Logic ---
    print("\n" + "="*80)
    save_file = input("Do you want to save your results to a file? (Y/N): ").strip().upper()
    
    if save_file == 'Y':
        save_all = input(f"Do you want to save ALL {len(viewed_cases)} random cases you just viewed? (Y/N): ").strip().upper()
        
        if save_all == 'Y':
            final_cases = viewed_cases
            header_title = f"Randomly Sampled Scenarios - Total: {len(final_cases)}"
            js_script = "setTimeout(function() { window.print(); }, 1000);" if len(final_cases) <= 60 else "console.log('Auto-print disabled.');"
            html_warning = "" if len(final_cases) <= 60 else '<div class="warning">⚠️ WARNING: You saved a large list. Please check page count before printing.</div>'
        else:
            final_cases = [] 
            header_title = ""
            js_script = "setTimeout(function() { window.print(); }, 1000);"
            html_warning = ""

        # File Naming
        print("\n" + "-"*40)
        custom_name = input("Enter a base file name (No extensions needed, or press Enter for 'matrix_results'): ").strip()
        if not custom_name:
            custom_name = "matrix_results"
        
        custom_name = custom_name.replace('.csv', '').replace('.html', '')
        
        counter = 1
        final_name = custom_name
        while os.path.exists(f"{final_name}.csv") or os.path.exists(f"{final_name}.html"):
            final_name = f"{custom_name}_Run{counter}"
            counter += 1

        csv_filename = f"{final_name}.csv"
        html_filename = f"{final_name}.html"

        # Save to CSV
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Embedding credits in the CSV file
            writer.writerow(["# ZWICKY BOX STORY GENERATOR (Classroom Edition)"])
            writer.writerow(["# developed by Keis Ohtsuka (c) 2026 using Google Gemini Pro."])
            writer.writerow(["# Creative Commons Attribution NonCommercial ShareAlike licence: CC BY NC SA 4.0"])
            writer.writerow([])
            writer.writerow(["# ORIGINAL ZWICKY MATRIX"])
            writer.writerow(columns)
            writer.writerows(formatted_data)
            writer.writerow([])
            
            writer.writerow(["# THE 5 CORE SCENARIOS (Without Replacement)"])
            writer.writerow(["Plot ID"] + columns)
            writer.writerow(["Plot 1 (Custom Locked-In)"] + student_scenario)
            for idx, case in enumerate(other_4_cases):
                writer.writerow([f"Plot {idx + 2}"] + list(case))
            
            if final_cases:
                writer.writerow([])
                writer.writerow([f"# {header_title.upper()}"])
                writer.writerow(["Plot ID"] + columns)
                for idx, case in enumerate(final_cases):
                    writer.writerow([f"Random Plot {idx + 1}"] + list(case))

        csv_filepath = os.path.abspath(csv_filename)
        html_filepath = os.path.abspath(html_filename)

        # Build HTML Tables
        core_html = "<table>\n<tr><th>Plot ID</th>"
        for col in columns:
            core_html += f"<th>{col}</th>"
        core_html += "</tr>\n"
        
        core_html += f"<tr class='custom-row'><td><strong>⭐ Plot 1 (Your Custom Scenario)</strong></td>"
        for item in student_scenario:
            core_html += f"<td>{item}</td>"
        core_html += "</tr>\n"
        
        for idx, case in enumerate(other_4_cases):
            core_html += f"<tr><td><strong>Plot {idx + 2}</strong></td>"
            for item in case:
                core_html += f"<td>{item}</td>"
            core_html += "</tr>\n"
        core_html += "</table>"

        extra_html = ""
        if final_cases:
            extra_html += f"<h2>{header_title}</h2>\n<table>\n<tr><th>Plot ID</th>"
            for col in columns:
                extra_html += f"<th>{col}</th>"
            extra_html += "</tr>\n"
            for idx, case in enumerate(final_cases):
                extra_html += f"<tr><td><strong>Random {idx + 1}</strong></td>"
                for item in case:
                    extra_html += f"<td>{item}</td>"
                extra_html += "</tr>\n"
            extra_html += "</table>"

        # HTML Generation
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Zwicky Box: {final_name}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px auto; max-width: 1000px; color: #333; line-height: 1.6; }}
                h1 {{ color: #2c3e50; margin-bottom: 5px; }}
                .credits {{ font-size: 13px; color: #7f8c8d; margin-top: 0; margin-bottom: 30px; font-style: italic; }}
                h2 {{ color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 5px; margin-top: 40px; }}
                .warning {{ color: #c0392b; font-weight: bold; background: #fadbd8; padding: 15px; border-left: 6px solid #c0392b; margin-bottom: 20px; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 15px; margin-bottom: 30px; font-size: 14px; }}
                th, td {{ border: 1px solid #bdc3c7; text-align: left; padding: 12px 10px; }}
                th {{ background-color: #ecf0f1; font-weight: bold; color: #2c3e50; }}
                tr:nth-child(even) {{ background-color: #fcfcfc; }}
                .custom-row {{ background-color: #d4efdf !important; border: 2px solid #27ae60; }}
                .file-note {{ font-size: 12px; color: #7f8c8d; text-align: right; }}
                @media print {{
                    .no-print {{ display: none; }}
                    body {{ margin: 0; max-width: 100%; }}
                    table {{ page-break-inside: auto; }}
                    tr {{ page-break-inside: avoid; page-break-after: auto; }}
                    th {{ background-color: #ecf0f1 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
                    .custom-row {{ background-color: #d4efdf !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
                }}
            </style>
            <script>
                window.onload = function() {{ {js_script} }};
            </script>
        </head>
        <body>
            <div class="file-note">File generated: {final_name}</div>
            {html_warning}
            
            <h1>Zwicky Box Story Generator</h1>
            <p class="credits">developed by Keis Ohtsuka (c) 2026 using Google Gemini Pro.<br>
            Creative Commons Attribution NonCommercial ShareAlike licence: CC BY NC SA 4.0</p>
            
            <h2>Original Zwicky Box Matrix</h2>
            <table>
                <tr>{"".join(f"<th>{col}</th>" for col in columns)}</tr>
                {"".join("<tr>" + "".join(f"<td>{item}</td>" for item in row) + "</tr>" for row in formatted_data)}
            </table>

            <h2>The 5 Core Scenarios (Without Replacement)</h2>
            <p>Plot 1 was interactively generated. Plots 2-5 were built using the remaining elements from your matrix.</p>
            {core_html}
            
            {extra_html}
            
        </body>
        </html>
        """

        with open(html_filename, mode='w', encoding='utf-8') as file:
            file.write(html_content)

        webbrowser.open('file://' + html_filepath)

        print("\n" + "="*80)
        print("SUCCESS! Your results have been saved and your webpage has been opened.")
        print("-" * 80)
        print(f"📊 Spreadsheet Data   : {csv_filename}  (Open this in Excel or Numbers)")
        print(f"🌐 Printable Web Page : {html_filename} (Open this in Chrome, Safari, etc.)")
        print("-" * 80)
        print(f"Folder Location: {os.path.dirname(csv_filepath)}")
        
    else:
        print("\nResults were NOT saved to a file.")

    print("="*80)
    input("Press ENTER to close this window...")

if __name__ == "__main__":
    main()
