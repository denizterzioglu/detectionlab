from app.utility.base_world import BaseWorld
from plugins.detectionlab.app.detectionlab_gui import DetectionLabGUI
from plugins.detectionlab.app.detectionlab_api import DetectionLabAPI

name = 'DetectionLab'
description = 'Automates the infrastructure deployment for a lab environment in Proxmox currently using Packer, Terraform, and Ansible'
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

