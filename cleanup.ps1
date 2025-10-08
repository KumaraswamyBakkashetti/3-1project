# Cleanup Script - Removes unnecessary files to keep project clean

Write-Host "=" -NoNewline; Write-Host ("="*69)
Write-Host "🧹 PROJECT CLEANUP SCRIPT"
Write-Host "=" -NoNewline; Write-Host ("="*69)

Write-Host "`n📊 Current Status:"
Write-Host "  Logs: " -NoNewline
$logCount = (Get-ChildItem logs\*.json -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host "$logCount files"

Write-Host "  Data files: " -NoNewline
$dataCount = (Get-ChildItem data\*.csv -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host "$dataCount files"

Write-Host "`n🗑️  What will be cleaned:"
Write-Host "  ✓ Old log files (keep only 5 most recent)"
Write-Host "  ✓ Temporary/test scripts"
Write-Host "  ✓ Duplicate training data CSVs"

$response = Read-Host "`nProceed with cleanup? (y/n)"
if ($response -ne 'y') {
    Write-Host "Cancelled."
    exit
}

Write-Host "`n🧹 Cleaning up..."

# 1. Clean old logs (keep 5 most recent)
Write-Host "`n1. Cleaning old log files..."
$runLogs = Get-ChildItem logs\run_*.json -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
if ($runLogs.Count -gt 5) {
    $runLogs | Select-Object -Skip 5 | Remove-Item -Force
    Write-Host "   ✓ Removed $($runLogs.Count - 5) old run logs"
} else {
    Write-Host "   ✓ No old run logs to remove"
}

$summaryLogs = Get-ChildItem logs\summary_*.json -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
if ($summaryLogs.Count -gt 5) {
    $summaryLogs | Select-Object -Skip 5 | Remove-Item -Force
    Write-Host "   ✓ Removed $($summaryLogs.Count - 5) old summary logs"
} else {
    Write-Host "   ✓ No old summary logs to remove"
}

# 2. Remove test/debug scripts (if they exist)
Write-Host "`n2. Removing test/debug scripts..."
$testFiles = @(
    "debug_llm_response.py",
    "test_api_fix.py", 
    "final_system_test.py",
    "quick_data_generation.py"
)

$removed = 0
foreach ($file in $testFiles) {
    if (Test-Path $file) {
        Remove-Item -Force $file
        $removed++
    }
}
if ($removed -gt 0) {
    Write-Host "   ✓ Removed $removed test scripts"
} else {
    Write-Host "   ✓ No test scripts to remove"
}

# 3. Clean duplicate virtual environment folders
Write-Host "`n3. Checking for duplicate virtual environments..."
if (Test-Path ".venv") {
    Remove-Item -Recurse -Force ".venv"
    Write-Host "   ✓ Removed duplicate .venv folder"
} else {
    Write-Host "   ✓ No duplicate venv folders"
}

# 4. Merge training data CSVs (if multiple exist)
Write-Host "`n4. Checking for duplicate data files..."
$trainingCSVs = Get-ChildItem data\features_training_*.csv -ErrorAction SilentlyContinue

if ($trainingCSVs.Count -gt 0) {
    Write-Host "   Found $($trainingCSVs.Count) training data file(s)"
    $response = Read-Host "   Merge into features.csv and delete? (y/n)"
    
    if ($response -eq 'y') {
        foreach ($csv in $trainingCSVs) {
            # Append content (skip header if it exists)
            $content = Get-Content $csv.FullName
            if ($content[0] -notmatch "^avg_personal_score") {
                # If first line is not header, append all
                Add-Content -Path "data\features.csv" -Value $content
            } else {
                # Skip header line
                $content | Select-Object -Skip 1 | Add-Content -Path "data\features.csv"
            }
            Remove-Item -Force $csv.FullName
            Write-Host "   ✓ Merged and removed $($csv.Name)"
        }
    }
} else {
    Write-Host "   ✓ No duplicate training data files"
}

# 5. Summary
Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline; Write-Host ("="*69)
Write-Host "✅ CLEANUP COMPLETE"
Write-Host "=" -NoNewline; Write-Host ("="*69)

Write-Host "`n📊 Final Status:"
$finalLogCount = (Get-ChildItem logs\*.json -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host "  Logs: $finalLogCount files (kept 5 most recent)"

$finalDataCount = (Get-ChildItem data\*.csv -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host "  Data files: $finalDataCount file(s)"

# Count total rows in features.csv
if (Test-Path "data\features.csv") {
    $rows = (Get-Content "data\features.csv" | Measure-Object -Line).Lines - 1
    Write-Host "  Training data rows: $rows"
}

Write-Host "`n📁 Essential files kept:"
Write-Host "  ✓ All source code (Agent_Monitor/, MAS/, Trainer/)"
Write-Host "  ✓ Configuration (.env, requirements.txt)"
Write-Host "  ✓ Documentation (README.md, *_SUMMARY.md)"
Write-Host "  ✓ Training data (data/features.csv)"
Write-Host "  ✓ Trained model (models/)"
Write-Host "  ✓ Recent logs (5 most recent)"

Write-Host "`n🚀 Your project is now clean and ready!"
Write-Host ""
