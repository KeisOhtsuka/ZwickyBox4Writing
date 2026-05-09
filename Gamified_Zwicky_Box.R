# Zwicky Box Story Generator (Classroom Edition)
# developed by Keis Ohtsuka (c) 2026 using Google Gemini Pro.
# Creative Commons Attribution NonCommercial ShareAlike licence: CC BY NC SA 4.0

# Instructions: Run this script in RStudio. 
# It will guide you through row-by-row entry and an interactive dice roll.

zwicky_box_app <- function() {
  columns_list <- c('Character(s)', 'Setting', 'Objects', 'Crisis', 'Action')
  col_letters <- c('A', 'B', 'C', 'D', 'E')
  
  # --- HEADER ---
  cat(paste0(rep("=", 80), collapse=""), "\n")
  cat("ZWICKY BOX STORY GENERATOR (Classroom Edition - R)\n")
  cat("developed by Keis Ohtsuka (c) 2026 using Google Gemini Pro.\n")
  cat("Creative Commons Attribution NonCommercial ShareAlike licence: CC BY NC SA 4.0\n")
  cat(paste0(rep("=", 80), collapse=""), "\n")
  
  # --- PHASE 1: ROW-BY-ROW INPUT ---
  cat("\nPHASE 1: BUILD YOUR MATRIX\n")
  cat("Please enter 5 rows of story elements.\n")
  
  matrix_data <- matrix("", nrow = 5, ncol = 5)
  colnames(matrix_data) <- columns_list
  
  for (r in 1:5) {
    cat(sprintf("\n--- Entering Elements for Row %d ---\n", r))
    for (c in 1:5) {
      repeat {
        val <- readline(prompt = sprintf("  %s: ", columns_list[c]))
        val <- trimws(val)
        if (val != "") {
          matrix_data[r, c] <- val
          break
        }
        cat("  ⚠️ Entry cannot be blank. Please try again.\n")
      }
    }
  }
  
  cat("\n✅ Matrix Complete!\n")
  print(matrix_data)
  
  # --- PHASE 2: THE GAMIFIED DICE ROLL ---
  cat("\n", paste0(rep("=", 80), collapse=""), "\n")
  cat("PHASE 2: THE DICE ROLL - BUILD YOUR CUSTOM SCENARIO!\n")
  cat(paste0(rep("=", 80), collapse=""), "\n")
  cat("Roll for each column. You can keep the result or roll again.\n")
  
  student_scenario <- character(5)
  remaining_items_list <- list()
  
  for (c in 1:5) {
    cat(sprintf("\n🎲 ROLLING FOR: %s\n", toupper(columns_list[c])))
    pool <- sample(matrix_data[, c]) # Shuffle the column
    rejected <- character(0)
    
    while (length(pool) > 0) {
      item <- pool[1]
      pool <- pool[-1]
      
      if (length(pool) == 0) {
        cat(sprintf("  ⚠️ Last option remaining! Auto-locking: %s\n", item))
        student_scenario[c] <- item
        remaining_items_list[[c]] <- rejected
        break
      }
      
      repeat {
        choice <- toupper(trimws(readline(prompt = sprintf("  Rolled: %s | Keep this? (Y/N): ", item))))
        if (choice %in% c('Y', 'N')) break
      }
      
      if (choice == 'Y') {
        student_scenario[c] <- item
        remaining_items_list[[c]] <- c(pool, rejected)
        cat(sprintf("  ✅ Locked in: %s\n", item))
        break
      } else {
        rejected <- c(rejected, item)
        cat("  🔄 Rolling again...\n")
      }
    }
  }
  
  cat("\n🎉 YOUR CUSTOM SCENARIO IS COMPLETE!\n")
  cat(paste(student_scenario, collapse=" / "), "\n")
  
  # Prepare the other 4 Core Scenarios (Without Replacement)
  other_4_plots <- matrix("", nrow = 4, ncol = 5)
  for (c in 1:5) {
    other_4_plots[, c] <- sample(remaining_items_list[[c]])
  }
  
  # --- PHASE 3: INFINITE EXPLORER ---
  cat("\n", paste0(rep("=", 80), collapse=""), "\n")
  cat("PHASE 3: EXPLORE RANDOM SCENARIOS (With Replacement)\n")
  cat(paste0(rep("=", 80), collapse=""), "\n")
  
  viewed_random <- list()
  case_count <- 0
  
  repeat {
    cat("\n")
    for (i in 1:20) {
      case_count <- case_count + 1
      rand_case <- sapply(1:5, function(c) sample(matrix_data[, c], 1))
      viewed_random[[case_count]] <- rand_case
      cat(sprintf("  Plot %03d | %s\n", case_count, paste(rand_case, collapse=" / ")))
    }
    
    more <- toupper(trimws(readline(prompt = "\nShow 20 more random samples? (Y/N): ")))
    if (more == "N") break
  }
  
  # --- PHASE 4: SAVE RESULTS ---
  cat("\n", paste0(rep("=", 80), collapse=""), "\n")
  save_choice <- toupper(trimws(readline(prompt = "Do you want to save your results to a file? (Y/N): ")))
  
  if (save_choice == "Y") {
    file_base <- readline(prompt = "Enter a filename (no extension): ")
    if (trimws(file_base) == "") file_base <- "zwicky_results"
    
    csv_name <- paste0(file_base, ".csv")
    html_name <- paste0(file_base, ".html")
    
    # 1. Save CSV
    con <- file(csv_name, open="wt")
    writeLines(c(
      "# ZWICKY BOX STORY GENERATOR (Classroom Edition)",
      "# developed by Keis Ohtsuka (c) 2026 using Google Gemini Pro.",
      "# Creative Commons Attribution NonCommercial ShareAlike licence: CC BY NC SA 4.0",
      "",
      "# ORIGINAL MATRIX"
    ), con)
    write.table(matrix_data, con, sep=",", row.names=F, col.names=T, append=T)
    writeLines(c("", "# THE 5 CORE SCENARIOS (Without Replacement)"), con)
    core_df <- data.frame(Plot_ID = c("Plot 1 (Custom)", "Plot 2", "Plot 3", "Plot 4", "Plot 5"),
                          rbind(student_scenario, other_4_plots))
    colnames(core_df) <- c("Plot ID", columns_list)
    write.table(core_df, con, sep=",", row.names=F, col.names=T, append=T)
    
    if (length(viewed_random) > 0) {
      writeLines(c("", "# RANDOM SAMPLES"), con)
      rand_df <- data.frame(Plot_ID = paste("Random", 1:length(viewed_random)),
                            do.call(rbind, viewed_random))
      colnames(rand_df) <- c("Plot ID", columns_list)
      write.table(rand_df, con, sep=",", row.names=F, col.names=T, append=T)
    }
    close(con)
    
    # 2. Save HTML
    html_rows <- paste0(apply(other_4_plots, 1, function(r) {
      paste0("<tr><td>Plot</td>", paste0("<td>", r, "</td>", collapse=""), "</tr>")
    }), collapse="\n")
    
    rand_html_rows <- ""
    if(length(viewed_random) > 0) {
      rand_html_rows <- paste0(sapply(1:length(viewed_random), function(i) {
        paste0("<tr><td>Random ", i, "</td>", paste0("<td>", viewed_random[[i]], "</td>", collapse=""), "</tr>")
      }), collapse="\n")
    }
    
    html_content <- sprintf("
    <!DOCTYPE html><html><head><title>Zwicky Results</title>
    <style>
      body { font-family: sans-serif; margin: 40px; color: #333; }
      table { border-collapse: collapse; width: 100%%; margin-bottom: 30px; }
      th, td { border: 1px solid #ccc; padding: 10px; text-align: left; }
      th { background: #eee; }
      .custom-row { background-color: #d4efdf; font-weight: bold; }
      .credits { font-size: 0.8em; color: #777; }
    </style></head><body>
      <h1>Zwicky Box Story Generator</h1>
      <p class='credits'>Developed by Keis Ohtsuka (c) 2026 using Google Gemini Pro.<br>CC BY NC SA 4.0</p>
      <h2>The Core Scenarios</h2>
      <table>
        <tr><th>ID</th><th>Character</th><th>Setting</th><th>Object</th><th>Crisis</th><th>Action</th></tr>
        <tr class='custom-row'><td>⭐ Plot 1</td>%s</tr>
        %s
      </table>
      <h2>Random Samples</h2>
      <table>%s</table>
    </body></html>", 
                            paste0("<td>", student_scenario, "</td>", collapse=""),
                            html_rows, rand_html_rows)
    
    writeLines(html_content, html_name)
    
    # Open Results
    cat(sprintf("\n✅ Saved to %s and %s\n", csv_name, html_name))
    utils::browseURL(html_name)
  }
  
  cat("\nApplication Finished. Press ENTER to close.")
  readline()
}

# Run the app
zwicky_box_app()
