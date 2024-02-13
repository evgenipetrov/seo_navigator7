# This script is used to prepare the development environment for a Django project.

# Load environment variables from .env file
Write-Host "Loading environment variables from .env file..."
$envFilePath = ".\.env"
Get-Content $envFilePath | ForEach-Object {
    $line = $_.Trim()
    if ($line -ne "")
    {
        $key, $value = $line -split '=', 2
        Set-Item -Path env:$key -Value $value
    }
}

# Ensure the Conda executable path is correct
if (-Not(Test-Path -Path $env:CONDA_EXE))
{
    Write-Host "Conda executable not found at $env:CONDA_EXE"
    exit 1
}

# Check if the Conda environment exists
$envList = & "$env:CONDA_EXE" env list
$envExists = $envList -like "*$env:CONDA_PREFIX*"

if (-Not$envExists)
{
    Write-Host "Conda environment $env:CONDA_PREFIX does not exist. Creating..."
    # Ensure there are no spaces around the '=' sign and use the full path for conda executable
    $condaCreateCommand = "$env:CONDA_EXE create --name $env:CONDA_PREFIX python=$env:PYTHON_VER -y"
    Write-Host "Running command: $condaCreateCommand"
    Invoke-Expression $condaCreateCommand
    if ($LASTEXITCODE -ne 0)
    {
        Write-Host "Failed to create Conda environment $env:CONDA_PREFIX" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}
else
{
    Write-Host "Conda environment $env:CONDA_PREFIX already exists. Skipping creation."
}


# Install Python packages from requirements.txt
Write-Host "Installing Python packages from requirements.txt..."
& "$env:CONDA_EXE" run -n $env:CONDA_PREFIX pip install -r requirements.txt

# Install Python packages from requirements.txt
Write-Host "Installing Python dev packages from dev.txt..."
& "$env:CONDA_EXE" run -n $env:CONDA_PREFIX pip install -r requirements.dev.txt

# Perform Django migrations
Write-Host "Performing Django migrations..."
& "$env:CONDA_EXE" run -n $env:CONDA_PREFIX python "$env:DJANGO_PROJECT_DIR\manage.py" makemigrations
& "$env:CONDA_EXE" run -n $env:CONDA_PREFIX python "$env:DJANGO_PROJECT_DIR\manage.py" migrate

# Check Docker build status
Write-Host "Checking Docker build status..."
if ($env:DOCKER_BUILD_ENABLED -eq "true")
{
    $dockerfilePath = "docker/${env:DOCKER_IMAGE_NAME}/Dockerfile"
    $imageName = "${env:DOCKER_IMAGE_NAME}:${env:SEO_SPIDER_VERSION}"
    Write-Host "Docker build is enabled. Building image $imageName..."
    $buildCommand = "docker build . -f `"$dockerfilePath`" --build-arg USER_NAME=`"$env:USERNAME`" --build-arg SEO_SPIDER_VERSION=`"$env:SEO_SPIDER_VERSION`" -t `"$imageName`""
    Invoke-Expression $buildCommand
    if ($LASTEXITCODE -ne 0)
    {
        Write-Host "Docker build failed" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

Write-Host "Environment setup is complete."

# End of setup-env.ps1
