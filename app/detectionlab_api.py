import json
import os
import subprocess
import asyncio
import shutil
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
        This sample endpoint mirrors the request body in its response.
        """
        request_body = json.loads(await request.read())
        return web.json_response(request_body)

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
        # Commands to check and their installation commands
        tools = {
            'terraform': {
                'name': 'Terraform',
                'install_command': 'sudo apt-get install -y terraform'
            },
            'ansible': {
                'name': 'Ansible',
                'install_command': 'sudo apt-get install -y ansible'
            },
            'az': {
                'name': 'Azure CLI',
                'install_command': 'curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash'
            }
        }

        # Check if all tools are installed
        for cmd, tool_info in tools.items():
            exists = shutil.which(cmd) is not None
            if not exists:
                print(f"{tool_info['name']} is not installed or not found in the PATH.")
                try:
                    # Attempt to install the missing tool
                    print(f"Attempting to install {tool_info['name']}...")
                    result = subprocess.run(tool_info['install_command'], shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    print(result.stdout.decode())
                    print(f"{tool_info['name']} installed successfully.")
                except subprocess.CalledProcessError as e:
                    print(f"Failed to install {tool_info['name']}. Error: {e.stderr.decode()}")
                    return f"Error: {tool_info['name']} could not be installed automatically."
        
        return "All prerequisites are met."

    async def update_azure_variables_and_run_scripts(self, request):
        """
        This endpoint updates the terraform.tfvars file, performs Azure authentication, and runs Terraform and Ansible scripts.
        """
        try:
            print('Azure deployment started')
            home = os.getenv("HOME")
            cwd = os.getcwd()
            plugin = f"{cwd}/plugins/detectionlab"

            # Handle multipart/form-data
            reader = await request.multipart()
            variables_data = {}

            # Temporary path to store uploaded SSH key file
            priv_ssh_key_path = None

            async for field in reader:
                if field.name == 'ssh_key':
                    filename = field.filename
                    priv_ssh_key_path = f"{home}/.ssh/{filename}"

                    with open(priv_ssh_key_path, 'wb+') as f:
                        while True:
                            chunk = await field.read_chunk()
                            if not chunk:
                                break
                            f.write(chunk)
                else:
                    variables_data[field.name] = await field.text()

            # Extract variables from the parsed data
            region = variables_data.get('region', 'germanywestcentral')
            public_key_name = variables_data.get('publicKeyName', 'id_logger')
            public_key_value = variables_data.get('publicKeyValue')
            public_ssh_key_path = f"{home}/.ssh/{public_key_name}.pub"
            ip_whitelist = variables_data.get('ipWhitelist')
            workspace_key = variables_data.get('workspaceKey')
            workspace_id = variables_data.get('workspaceID')
            tenant_id = variables_data.get('tenantID')
            client_id = variables_data.get('clientID')
            client_secret = variables_data.get('clientSecret')
            subscription_id = variables_data.get('subscriptionID')

            print('Variables extracted')

            with open(public_ssh_key_path, "w+") as f:
                f.write(public_key_value)

            # Check prerequisites
            prerequisite_check = await self.check_prerequisites()
            if "Error" in prerequisite_check:
                return web.json_response({'success': False, 'error': prerequisite_check})
            
            print('Pre-req checks successfull')

            # Path to the terraform.tfvars file
            variables_path = os.path.join(os.path.dirname(__file__), '../data/azure/Terraform/terraform.tfvars')

            # Write the data to terraform.tfvars
            with open(variables_path, 'w+') as tfvars_file:
                tfvars_file.write(f"""
region                 = "{region}"
public_key_name         = "{public_key_name}"
public_key_path         = "{public_ssh_key_path}"
private_key_path        = "{priv_ssh_key_path}"
ip_whitelist           = {ip_whitelist}
subscription_id         = "{subscription_id}"
""")
                
                if workspace_key and workspace_id:
                    tfvars_file.write(f"""
# Added the following lines for your key because you want to use Azure Log Analytics and Azure Sentinel
workspace_key          = "{workspace_key}"
workspace_id           = "{workspace_id}"
""")        

            print('Variables written')

            # Shell script path
            shell_script_path = os.path.join(os.path.dirname(__file__), '../data/azure/run_azure_setup.sh')

            # Execute the shell script to handle Azure auth, Terraform, and Ansible
            process = await asyncio.create_subprocess_exec(
                'bash', shell_script_path,
                tenant_id, client_id, client_secret,
                f"{plugin}/data/azure/Terraform",
                f"{plugin}/data/azure/Ansible",
                f"{plugin}/data/azure/build_ansible_inventory.sh",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                return web.json_response({
                    'success': False,
                    'error': f'Script execution failed with error: {stderr.decode("utf-8")}'
                })

            return web.json_response({'success': True, 'output': stdout.decode('utf-8')})

        except Exception as e:
            return web.json_response({'success': False, 'error': str(e)})


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

    