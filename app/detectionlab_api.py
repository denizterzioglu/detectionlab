import json
import os
import subprocess
import asyncio
import shutil
import logging
from pathlib import Path
from aiohttp import web
from aiohttp_jinja2 import template
from app.service.auth_svc import for_all_public_methods, check_authorization

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

home = os.getenv("HOME")
cwd = os.getcwd()
plugin = f"{cwd}/plugins/detectionlab"

@for_all_public_methods(check_authorization)
class DetectionLabAPI:

    def __init__(self, services):
        self.services = services
        self.auth_svc = self.services.get('auth_svc')
        self.data_svc = self.services.get('data_svc')

        # Initial state (equivalent to Pinia store)
        self.state = {
            "isLoading": False,
            "isGenerated": False,
            "generatedPlatform": ''
        }

    @template('detectionlab.html')
    async def mirror(self, request):
        """
        This sample endpoint mirrors the request body in its response.
        """
        request_body = json.loads(await request.read())
        return web.json_response(request_body)

    async def get_lab_state(self, request):
        """
        API endpoint to get the current state of the lab.
        """
        try:
            logger.info("Fetching lab state")
            logger.info(self.state)
            return web.json_response(self.state)
        except Exception as e:
            logger.error(f"Error fetching lab state: {e}")
            return web.json_response({"error": "Internal Server Error"}, status=500)

    async def get_azure_terraform_output(self, request):
        """
        API endpoint to get the access points to the tools
        """
        try:
            # Define the directory where terraform is located
            terraform_directory = os.path.join(os.getcwd(), 'plugins/detectionlab/data/azure/Terraform')
            
            logger.info(f"Taking outputs from: {terraform_directory}")


            # Run the terraform output command
            command = ['terraform', 'output', '-json']
            result = subprocess.run(command, cwd=terraform_directory, capture_output=True, text=True, check=True)

            # Parse the JSON output from Terraform
            terraform_output = json.loads(result.stdout)

            logger.info(terraform_output)

            # Extract necessary fields from the output
            output_dict = {
                'dcPublicIp': terraform_output.get('dc_public_ip', {}).get('value', ''),
                'fleetUrl': terraform_output.get('fleet_url', {}).get('value', ''),
                'guacamoleUrl': f"{terraform_output.get('guacamole_url', {}).get('value', '')}/#/?username=vagrant&password=vagrant",
                'loggerPublicIp': terraform_output.get('logger_public_ip', {}).get('value', ''),
                'region': terraform_output.get('region', {}).get('value', ''),
                'splunkUrl': terraform_output.get('splunk_url', {}).get('value', ''),
                'velociraptorUrl': terraform_output.get('velociraptor_url', {}).get('value', ''),
                'wefPublicIp': terraform_output.get('wef_public_ip', {}).get('value', ''),
                'win10PublicIp': terraform_output.get('win10_public_ip', {}).get('value', '')
            }

            # Return or print the extracted data as JSON
            return web.json_response(output_dict)

        except subprocess.CalledProcessError as e:
            print(f"Error running terraform: {e}")
            return web.json_response({"error": "Internal Server Error"}, status=500)
        except Exception as e:
            print(f"General error: {e}")
            return web.json_response({"error": "Internal Server Error"}, status=500)

    async def delete_lab(self, request):
        """
        API endpoint to delete the lab and reset the lab state.
        """
        logger.info(f"Deprovisioning the lab on {self.state['generatedPlatform']}")
        
        if self.state['generatedPlatform'] == 'Azure': 
            command = 'echo y | az group delete --name DetectionLab-terraform'
            
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)   
            
            stdout, stderr = await asyncio.to_thread(process.communicate)
            
            if process.returncode != 0:
                logger.error(f'Command "{command}" failed with error: {stderr.decode("utf-8")}')
                return web.json_response({
                    'success': False,
                    'error': f'Command "{command}" failed with error: {stderr.decode("utf-8")}'
                })
            else:
                logger.info(f'Command "{command}" completed successfully')
                logger.debug(f'STDOUT: {stdout.decode("utf-8").strip()}')
                logger.debug(f'STDERR: {stderr.decode("utf-8").strip()}')
                
            logger.info('Azure resources were deleted')
            
        # Reset lab state
        self.state["isLoading"] = False
        self.state["isGenerated"] = False
        self.state["generatedPlatform"] = None
        logger.info('Lab state has been reset.')
        
        return web.json_response({'success': True, 'state': self.state})


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

        for cmd, tool_info in tools.items():
            exists = shutil.which(cmd) is not None
            if not exists:
                logger.warning(f"{tool_info['name']} is not installed or not found in the PATH.")
                try:
                    logger.info(f"Attempting to install {tool_info['name']}...")
                    result = subprocess.run(
                        tool_info['install_command'], 
                        shell=True, 
                        check=True, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE
                    )
                    logger.info(result.stdout.decode())
                    logger.info(f"{tool_info['name']} installed successfully.")
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to install {tool_info['name']}. Error: {e.stderr.decode()}")
                    return f"Error: {tool_info['name']} could not be installed automatically."

        return "All prerequisites are met."

    async def generate_azure_lab(self, request):
        """
        This endpoint updates the terraform.tfvars file, performs Azure authentication, and runs Terraform and Ansible scripts.
        """
        try:
            logger.info('Azure deployment started')

            self.state["isLoading"] = True
            self.state["generatedPlatform"] = 'Azure'

            # Handle multipart/form-data
            reader = await request.multipart()
            variables_data = {}

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

            logger.info('Variables extracted')

            with open(public_ssh_key_path, "w+") as f:
                f.write(public_key_value)

            prerequisite_check = await self.check_prerequisites()
            if "Error" in prerequisite_check:
                return web.json_response({'success': False, 'error': prerequisite_check})
            
            logger.info('Pre-req checks successful')

            variables_path = os.path.join(os.path.dirname(__file__), '../data/azure/Terraform/terraform.tfvars')

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
workspace_key          = "{workspace_key}"
workspace_id           = "{workspace_id}"
""")

            logger.info('Variables written')

            shell_script_path = os.path.join(os.path.dirname(__file__), '../data/azure/run_azure_setup.sh')

            # Start subprocess to run the shell script
            process = await asyncio.create_subprocess_exec(
                'bash', shell_script_path,
                tenant_id, client_id, client_secret,
                f"{plugin}/data/azure/Terraform",
                f"{plugin}/data/azure/Ansible",
                f"{plugin}/data/azure/build_ansible_inventory.sh",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            logger.info('Shell script execution started')

            # Process stdout and stderr concurrently
            async def read_stream(stream, log_func):
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    log_func(line.decode().strip())

            stdout_task = asyncio.create_task(read_stream(process.stdout, logger.info))
            stderr_task = asyncio.create_task(read_stream(process.stderr, logger.error))

            # Wait for both tasks and the process to finish
            await asyncio.gather(stdout_task, stderr_task, process.wait())

            if process.returncode != 0:
                return web.json_response({
                    'success': False,
                    'error': 'Script execution failed. Check logs for details.'
                })

            logger.info('Shell script executed successfully.')
            self.state["isGenerated"] = True
            self.state["isLoading"] = False
            return web.json_response({'success': True, 'output': 'Script executed successfully'})

        except Exception as e:
            logger.exception('An error occurred during the Azure deployment process.')
            return web.json_response({'success': False, 'error': str(e)})

    async def generate_proxmox_lab(self, request):
        """
        This endpoint updates the variables.json file and runs the necessary shell scripts
        """
        try:
            # Log that the request is being processed
            logger.info('Processing request to generate Proxmox lab')

            # Parse the JSON request body
            variables_data = await request.json()
            logger.info('Received variables data')

            # Path to the variables.json file
            variables_path = os.path.join(os.path.dirname(__file__), '../data/proxmox/Packer/variables.json')

            # Write the data to variables.json
            with open(variables_path, 'w') as json_file:
                json.dump(variables_data, json_file, indent=2)
            logger.info(f'Updated variables.json at {variables_path}')

            # Change directory to Packer folder
            subprocess.Popen('cd ../data/proxmox/Packer', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Define the shell commands to run
            commands = [
                'PACKER_CACHE_DIR=../../Packer/packer_cache packer build -var-file variables.json windows_10_proxmox.json',
                'PACKER_CACHE_DIR=../../Packer/packer_cache packer build -var-file variables.json windows_2016_proxmox.json',
                'PACKER_CACHE_DIR=../../Packer/packer_cache packer build -var-file variables.json ubuntu2004_proxmox.json'
            ]
            
            # Log the commands that will be executed
            logger.info('Starting Packer build commands in parallel')

            # Start all commands in parallel
            processes = [subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for command in commands]

            # Collect all results
            for command, process in zip(commands, processes):
                stdout, stderr = await asyncio.to_thread(process.communicate)
                if process.returncode != 0:
                    logger.error(f'Command "{command}" failed with error: {stderr.decode("utf-8")}')
                    return web.json_response({
                        'success': False,
                        'error': f'Command "{command}" failed with error: {stderr.decode("utf-8")}'
                    })
                else:
                    logger.info(f'Command "{command}" completed successfully')
                    logger.debug(f'STDOUT: {stdout.decode("utf-8").strip()}')
                    logger.debug(f'STDERR: {stderr.decode("utf-8").strip()}')

            # Change directory to Terraform folder
            subprocess.Popen('cd ../Terraform', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info('Moved to Terraform directory')

            # Final successful response
            logger.info('Proxmox lab generation completed successfully')
            return web.json_response({'success': True})

        except Exception as e:
            logger.exception(f'Failed to generate Proxmox lab: {str(e)}')
            return web.json_response({'success': False, 'error': str(e)})
        