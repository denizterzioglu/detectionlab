import json
import os
import subprocess
import asyncio
from pathlib import Path
from aiohttp import web
from aiohttp_jinja2 import template
from app.service.auth_svc import for_all_public_methods, check_authorization

@for_all_public_methods(check_authorization)
class DetectionLabAPI:

    def __init__(self, services):
        self.services = services
        self.auth_svc = self.services.get('auth_svc')
        self.data_svc = self.services.get('data_svc')

    @template('detectionlab.html')
    async def mirror(self, request):
        """
        This sample endpoint mirrors the request body in its response
        """
        request_body = json.loads(await request.read())
        return web.json_response(request_body)

    def check_command(self, command: str) -> bool:
        """
        Check if a command is available in the system's PATH.
        """
        return subprocess.call(f"command -v {command}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

    def check_ssh_keypair(self, keypair_path: str) -> bool:
        """
        Check if the SSH keypair files exist at the specified path.
        """
        private_key_path = Path(keypair_path)
        public_key_path = Path(f"{keypair_path}.pub")
        return private_key_path.is_file() and public_key_path.is_file()

    async def check_prerequisites(self):
        """
        Check if all prerequisites are met:
        - Terraform installed and in PATH
        - Ansible installed and in PATH
        - Azure CLI installed and in PATH
        - SSH keypair exists
        """
        # Commands to check
        tools = {
            'terraform': 'Terraform',
            'ansible': 'Ansible',
            'az': 'Azure CLI'
        }

        # Check if all tools are installed
        for cmd, tool_name in tools.items():
            if not self.check_command(cmd):
                return f"Error: {tool_name} is not installed or not found in the PATH."
        
        # Check SSH keypair
        ssh_keypair_path = '/home/user/.ssh/id_logger'  # Adjust this path as needed
        if not self.check_ssh_keypair(ssh_keypair_path):
            return f"Error: SSH keypair not found at {ssh_keypair_path}."

        return "All prerequisites are met."

    async def update_proxmox_variables_and_run_scripts(self, request):
        """
        This endpoint updates the variables.json file and runs the necessary shell scripts
        """
        try:
            # Parse the JSON request body
            variables_data = await request.json()

            # Path to the variables.json file
            variables_path = os.path.join(os.path.dirname(__file__), '../data/proxmox/Packer/variables.json')

            # Write the data to variables.json
            with open(variables_path, 'w') as json_file:
                json.dump(variables_data, json_file, indent=2)

            subprocess.Popen('cd ../data/proxmox/Packer', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Define the shell commands to run
            commands = [
                'PACKER_CACHE_DIR=../../Packer/packer_cache packer build -var-file variables.json windows_10_proxmox.json',
                'PACKER_CACHE_DIR=../../Packer/packer_cache packer build -var-file variables.json windows_2016_proxmox.json',
                'PACKER_CACHE_DIR=../../Packer/packer_cache packer build -var-file variables.json ubuntu2004_proxmox.json'
            ]

            # Start all commands in parallel
            processes = [subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for command in commands]

            # Collect all results
            for process in processes:
                stdout, stderr = await asyncio.to_thread(process.communicate)
                if process.returncode != 0:
                    return web.json_response({
                        'success': False,
                        'error': f'Command failed with error: {stderr.decode("utf-8")}'
                    })
            
            subprocess.Popen('cd ../Terraform', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            return web.json_response({'success': True})

        except Exception as e:
            return web.json_response({'success': False, 'error': str(e)})

    async def update_azure_variables_and_run_scripts(self, request):
        """
        This endpoint updates the terraform.tfvars file, performs Azure authentication, and runs Terraform and Ansible scripts.
        """
        try:
            # Parse the JSON request body
            variables_data = await request.json()

            # Extract variables from the request
            region = variables_data.get('region', 'germany')
            public_key_name = variables_data.get('publicKeyName', 'id_logger')
            public_key_path = variables_data.get('publicKeyPath', '/home/user/.ssh/id_logger.pub')
            private_key_path = variables_data.get('privateKeyPath', '/home/user/.ssh/id_logger.pub')
            ip_whitelist = variables_data.get('ipWhitelist')
            workspace_key = variables_data.get('workspaceKey')
            workspace_id = variables_data.get('workspaceID')
            tenant_id = variables_data.get('tenantID')
            client_id = variables_data.get('clientID')
            client_secret = variables_data.get('clientSecret')

            # Check prerequisites
            prerequisite_check = await self.check_prerequisites()
            if "Error" in prerequisite_check:
                return web.json_response({'success': False, 'error': prerequisite_check})

            # Path to the terraform.tfvars file
            variables_path = os.path.join(os.path.dirname(__file__), '../data/azure/Terraform/terraform.tfvars')

            # Write the data to terraform.tfvars
            with open(variables_path, 'w') as tfvars_file:
                tfvars_file.write(f"""
region                 = "{region}"
public_key_name         = "{public_key_name}"
public_key_path         = "{public_key_path}"
private_key_path        = "{private_key_path}"
ip_whitelist           = {ip_whitelist}
""")
                
                # Conditionally include workspace_key and workspace_id
                if workspace_key and workspace_id:
                    tfvars_file.write(f"""
# Uncomment the following lines and add your key if you want to use Azure Log Analytics and Azure Sentinel
workspace_key          = "{workspace_key}"
workspace_id           = "{workspace_id}"
""")

            # Define shell commands for Terraform and Azure
            terraform_dir = '../data/azure/Terraform'
            terraform_commands = [
                'terraform init',
                'terraform apply --auto-approve'
            ]
            
            # Command to authenticate with Azure
            async def authenticate_azure():
                if tenant_id and client_id and client_secret:
                    auth_command = f'az login --service-principal --username {client_id} --password {client_secret} --tenant {tenant_id}'
                    process = await asyncio.create_subprocess_shell(
                        auth_command,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await process.communicate()
                    if process.returncode != 0:
                        return f'Azure authentication failed with error: {stderr.decode("utf-8")}'
                    return 'Azure authentication successful!'
                return 'Azure credentials are not provided.'

            # Function to run a shell command
            async def run_command(command, cwd=None):
                process = await asyncio.create_subprocess_shell(
                    command,
                    cwd=cwd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                return process.returncode, stdout.decode('utf-8'), stderr.decode('utf-8')

            # Authenticate to Azure
            auth_message = await authenticate_azure()
            if "failed" in auth_message:
                return web.json_response({'success': False, 'error': auth_message})

            # Run Terraform commands
            terraform_tasks = [run_command(cmd, cwd=terraform_dir) for cmd in terraform_commands]
            terraform_results = await asyncio.gather(*terraform_tasks)

            for returncode, stdout, stderr in terraform_results:
                if returncode != 0:
                    return web.json_response({
                        'success': False,
                        'error': f'Terraform command failed with error: {stderr}'
                    })

            # Provisioning with Ansible
            ansible_dir = '../data/azure/Ansible'
            ansible_commands = [
                'ansible-playbook -v detectionlab.yml --tags "dc"',
                'ansible-playbook -v detectionlab.yml --tags "wef"',
                'ansible-playbook -v detectionlab.yml --tags "win10"'
            ]
            
            # Run Ansible commands
            ansible_tasks = [run_command(cmd, cwd=ansible_dir) for cmd in ansible_commands]
            ansible_results = await asyncio.gather(*ansible_tasks)

            for returncode, stdout, stderr in ansible_results:
                if returncode != 0:
                    return web.json_response({
                        'success': False,
                        'error': f'Ansible command failed with error: {stderr}'
                    })

            return web.json_response({'success': True})

        except Exception as e:
            return web.json_response({'success': False, 'error': str(e)})

