# Function to print error message and exit
function Error-Exit {
    param([string]$message)
    Write-Error "[ERROR] $message"
    exit 1
}

# Function to check if a command exists
function Command-Exists {
    param([string]$command)
    $result = Get-Command $command -ErrorAction SilentlyContinue
    return $result -ne $null
}

# Function to install Python3 if not installed
function Install-Python3 {
    if (-not (Command-Exists python)) {
        Write-Output "Python3 is not installed. Installing..."
        # Download and install Python (adjust URL if needed)
        $url = "https://www.python.org/ftp/python/3.10.12/python-3.10.12-amd64.exe"
        $installer = "$env:TEMP\python-installer.exe"
        Invoke-WebRequest -Uri $url -OutFile $installer
        Start-Process -FilePath $installer -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
        Remove-Item $installer -Force
        if (-not (Command-Exists python)) {
            Error-Exit "Failed to install Python3."
        }
    } else {
        Write-Output "Python3 is already installed."
    }
}

# Function to install pip3 if not installed
function Install-Pip3 {
    if (-not (Command-Exists pip)) {
        Write-Output "pip3 is not installed. Installing..."
        python -m ensurepip
        python -m pip install --upgrade pip
        if (-not (Command-Exists pip)) {
            Error-Exit "Failed to install pip3."
        }
    } else {
        Write-Output "pip3 is already installed."
    }
}

# Function to create a virtual environment and install dependencies
function Create-Venv {
    Write-Output "Creating virtual environment..."
    python -m venv venv
    if (-not (Test-Path "venv")) {
        Error-Exit "Failed to create virtual environment."
    }

    Write-Output "Activating virtual environment..."
    $activateScript = ".\venv\Scripts\Activate.ps1"
    if (-not (Test-Path $activateScript)) {
        Error-Exit "Failed to find activate script."
    }
    . $activateScript

    if (-not (Test-Path "requirements.txt")) {
        Error-Exit "requirements.txt not found. Cannot install dependencies."
    }

    Write-Output "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Error-Exit "Failed to install dependencies."
    }

    Write-Output "Virtual environment created and dependencies installed successfully."
}

# Check if Python3 is installed, if not, install it
Install-Python3

# Check if pip3 is installed, if not, install it
Install-Pip3

# Check if venv directory exists
if (-not (Test-Path "venv")) {
    Write-Output "Virtual environment 'venv' not found. Creating a new one..."
    Create-Venv
} else {
    Write-Output "Virtual environment 'venv' already exists."
}

Write-Output "Setup completed successfully."
