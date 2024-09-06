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
    tags=$2
    
    echo "Running Ansible playbook with tags '$tags'..."
    cd "$ansible_dir"
    
    ansible-playbook -v detectionlab.yml --tags "$tags"
    
    echo "Ansible playbook with tags '$tags' complete."
}

# Main script execution
main() {
    tenant_id=$1
    client_id=$2
    client_secret=$3
    terraform_dir=$4
    ansible_dir=$5
    inventory_script=$6
    
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
    
    # Start the DC playbook
    run_ansible "$ansible_dir" "dc" &
    dc_playbook_pid=$!
    
    # Wait for 5 minutes
    echo "Waiting for 5 minutes before starting WEF and WIN10 provisioning..."
    sleep 300
    
    # Start WEF and WIN10 playbooks
    echo "Running WEF and WIN10 playbooks..."
    run_ansible "$ansible_dir" "wef" &
    run_ansible "$ansible_dir" "win10" &
    
    # Wait for all background jobs to finish
    wait $dc_playbook_pid
    
    echo "Ansible provisioning complete."
}

# Run main with all arguments
main "$@"
