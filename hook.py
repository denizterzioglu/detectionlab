from app.utility.base_world import BaseWorld
from plugins.detectionlab.app.detectionlab_gui import DetectionLabGUI
from plugins.detectionlab.app.detectionlab_api import DetectionLabAPI

name = 'DetectionLab'
description = 'Automates the infrastructure deployment for a lab environment in currently Proxmox using Packer, Vagrant, Terraform, and Ansible'
address = '/plugin/detectionlab/gui'
access = BaseWorld.Access.RED


async def enable(services):
    app = services.get('app_svc').application
    detectionlab_gui = DetectionLabGUI(services, name=name, description=description)
    app.router.add_static('/detectionlab', 'plugins/detectionlab/static/', append_version=True)
    app.router.add_route('GET', '/plugin/detectionlab/gui', detectionlab_gui.splash)

    detectionlab_api = DetectionLabAPI(services)
    # Add API routes here
    app.router.add_route('POST', '/plugin/detectionlab/mirror', detectionlab_api.mirror)
    app.router.add_route('POST', '/plugin/detectionlab/update-proxmox-variables', detectionlab_api.update_proxmox_variables_and_run_scripts)
    app.router.add_route('POST', '/plugin/detectionlab/update-azure-variables', detectionlab_api.update_azure_variables_and_run_scripts)
    app.router.add_route('GET', '/plugin/detectionlab/azure-terraform-output', detectionlab_api.get_azure_terraform_output)
