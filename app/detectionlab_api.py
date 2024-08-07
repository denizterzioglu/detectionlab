import json
import os
import subprocess
import asyncio
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

    async def update_variables_and_run_scripts(self, request):
        """
        This endpoint updates the variables.json file and runs the necessary shell scripts
        """
        try:
            # Parse the JSON request body
            variables_data = await request.json()

            # Path to the variables.json file
            variables_path = os.path.join(os.path.dirname(__file__), '../data/Packer/variables.json')

            # Write the data to variables.json
            with open(variables_path, 'w') as json_file:
                json.dump(variables_data, json_file, indent=2)

            subprocess.Popen('cd ../data/Packer', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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

            return web.json_response({'success': True})

        except Exception as e:
            return web.json_response({'success': False, 'error': str(e)})