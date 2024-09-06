#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Azure authentication function
authenticate_azure() {
    tenant_id=$1
    client_id=$2
    client_secret=$3
    
    if [[ -n "$tenant_id" && -n "$client_id" && -n "$client_secret" ]]; then
        echo "Authenticating with Azure..."
        az login --service-principal --username "$client_id" --password "$client_secret" --tenant "$tenant_id"
        echo "Azure authentication successful!"
    else
        echo "Azure credentials are not provided."
        exit 1
    fi
}

# Run Terraform commands
run_terraform() {
    terraform_dir=$1
    
    echo "Initializing Terraform..."
    cd "$terraform_dir"
    terraform init
    echo "Terraform init complete."
    
    echo "Applying Terraform configuration..."
    terraform apply --auto-approve
    echo "Terraform apply complete."
}

# Run Ansible commands
run_ansible() {
    ansible_dir=$1
    
    echo "Running Ansible playbooks..."
    cd "$ansible_dir"
    
    ansible-playbook -v detectionlab.yml --tags "dc"
    ansible-playbook -v detectionlab.yml --tags "wef"
    ansible-playbook -v detectionlab.yml --tags "win10"
    
    echo "Ansible provisioning complete."
}

# Main script execution
main() {
    tenant_id=$1
    client_id=$2
    client_secret=$3
    terraform_dir=$4
    ansible_dir=$5
    inventory_script=$6
    dotnet_script=$7

    # .NET installation
    
    chmod +x "$dotnet_script"
    "$dotnet_script" --version latest
    
    # Authenticate to Azure
    authenticate_azure "$tenant_id" "$client_id" "$client_secret"
    
    # Run Terraform
    run_terraform "$terraform_dir"
    
    # Wait for resources to be fully created (adjust time as necessary)
    echo "Waiting for resources to be fully created..."
    sleep 150
    
    # Configure inventory for Ansible (can commented out because main.tf:611 does this)
    echo "Configuring Ansible inventory..."
    chmod +x "$inventory_script"
    cd ..
    "$inventory_script"

    pip install pywinrm
    
    # Run Ansible
    run_ansible "$ansible_dir"
}

# Run main with all arguments
main "$@"
