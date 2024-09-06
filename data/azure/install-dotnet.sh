#!/bin/bash

# Variables
DOTNET_SCRIPT_URL="https://dot.net/v1/dotnet-install.sh"
SCRIPT_NAME="dotnet-install.sh"
CHANNEL="8.0"   # Default to .NET 8.0 SDK
VERSION="latest"
RUNTIME=""

# Function to display help
show_help() {
  echo "Usage: $0 [-s] [-r aspnetcore] [-v version] [-c channel]"
  echo ""
  echo "Options:"
  echo "  -s             Install the SDK (default)"
  echo "  -r runtime     Install .NET runtime instead of SDK (e.g., aspnetcore)"
  echo "  -v version     Install a specific version (default: latest)"
  echo "  -c channel     Specify the .NET channel (default: 8.0 for SDK)"
  echo ""
}

# Parse command-line arguments
while getopts "r:v:c:h" opt; do
  case "$opt" in
    r) RUNTIME="--runtime $OPTARG";;
    v) VERSION="$OPTARG";;
    c) CHANNEL="$OPTARG";;
    h) show_help; exit 0;;
    *) show_help; exit 1;;
  esac
done

# Download the .NET installation script
echo "Downloading .NET installation script..."
wget $DOTNET_SCRIPT_URL -O $SCRIPT_NAME

# Check if the script was downloaded successfully
if [ ! -f $SCRIPT_NAME ]; then
  echo "Failed to download the .NET installation script."
  exit 1
fi

# Make the script executable
chmod +x ./$SCRIPT_NAME

# Install .NET SDK or runtime based on user input
if [ -z "$RUNTIME" ]; then
  echo "Installing .NET SDK version $VERSION from channel $CHANNEL..."
  ./$SCRIPT_NAME --version $VERSION --channel $CHANNEL
else
  echo "Installing .NET runtime version $VERSION ($RUNTIME)..."
  ./$SCRIPT_NAME --version $VERSION $RUNTIME
fi

# Capture the exit code of the installation
EXIT_CODE=$?

# Clean up the script after installation
rm ./$SCRIPT_NAME

if [ $EXIT_CODE -eq 0 ]; then
  echo "Installation complete."
else
  echo "Installation failed with exit code $EXIT_CODE."
fi

exit $EXIT_CODE
