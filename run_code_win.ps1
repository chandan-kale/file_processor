# Function to print error message and exit
function Error-Exit {
    param (
        [string]$message
    )
    Write-Error $message
    exit 1
}

# Function to run the setup_venv.ps1 script
function Run-SetupVenv {
    Write-Output "Virtual environment 'venv' not found. Running setup_venv.ps1 to create it..."
    .\setup_venv.ps1 -ErrorAction Stop
}

# Check if venv directory exists
if (-not (Test-Path -Path "venv")) {
    Run-SetupVenv
}

# Activate the virtual environment
$venvActivateScript = ".\venv\Scripts\Activate.ps1"
if (Test-Path $venvActivateScript) {
    . $venvActivateScript
} else {
    Error-Exit "Failed to activate the virtual environment."
}

# Check if the main.py file exists
if (-not (Test-Path -Path "main.py")) {
    Error-Exit "main.py not found in the current directory."
}

# Run the Python script and capture its exit status
python main.py
$pythonExitStatus = $LASTEXITCODE

# Deactivate the virtual environment
deactivate

# Check if Python script execution was successful
if ($pythonExitStatus -ne 0) {
    Error-Exit "Python script 'main.py' failed with exit status $pythonExitStatus."
} else {
    Write-Output "Script executed successfully."
}
