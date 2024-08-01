# DetectionLab based on MITRE SKELETON

DetectionLab is/as a CALDERA plugin that automates the infrastructure deployment for a lab environment in currently Proxmox using Packer, Vagrant, Terraform, and Ansible


# Proxmox

### Intro [<i class="fas fa-link fa-lg"></i>](https://detectionlab.network/deployment/proxmox/#intro)

Proxmox support for DetectionLab was a recent addition before it was discontinued and requires more testing to ensure its stability and usability.

A big thank you to [@sukster](https://github.com/sukster) for adding this in [PR #737](https://github.com/clong/DetectionLab/pull/737).

> **Note:** He does not officially support or troubleshoot DetectionLab issues using the Proxmox provider. You’re welcome to open issues for community support, but he will not personally be able to assist with them.

### Prereqs (~30-60 minutes) [<i class="fas fa-link fa-lg"></i>](https://detectionlab.network/deployment/proxmox/#prereqs-30-60-minutes)

1. Have a Proxmox VE instance installed. This implementation was built and tested on Proxmox 7.x but may work with older versions of Proxmox.
2. Terraform version 0.13 or higher is required as it provides support for installing Terraform providers directly from the Terraform Registry.
3. The Proxmox Terraform Provider by Telmate [https://github.com/Telmate/terraform-provider-proxmox](https://github.com/Telmate/terraform-provider-proxmox) is required but will be installed automatically during a later step. For additional customization, the documentation for the provider is here: [https://registry.terraform.io/providers/Telmate/proxmox/latest/docs/resources/vm_qemu](https://registry.terraform.io/providers/Telmate/proxmox/latest/docs/resources/vm_qemu).
4. Your Proxmox instance must have at least two separate networks connected by bridges. First network (vmbr0) that is accessible from your current machine and has internet connectivity and a second HostOnly network (vmbr1) to allow the VMs to communicate over a private network. The network connected to vmbr0 that provides DHCP and internet connectivity must also be reachable from the host that is running Terraform - ensure your firewall is configured to allow this.
5. Install Ansible and pywinrm via `pip3 install ansible pywinrm –user` or by creating and using a virtual environment.
6. Packer v1.7.0+ must be installed and in your PATH.
7. sshpass must be installed to allow Ansible to use password login. On MacOS, install via `brew install hudochenkov/sshpass/sshpass` as `brew install sshpass` does not allow it to be installed.

### Steps [<i class="fas fa-link fa-lg"></i>](https://detectionlab.network/deployment/proxmox/#steps)

1. **(5 Minutes)** Edit the variables in `data/Packer/variables.json` to match your Proxmox configuration. The `proxmox_network_with_dhcp_and_internet` variable refers to any Proxmox network that will be able to provide DHCP and internet access to the VM while it’s being built in Packer. The `provisioning_machine_ip` variable refers to the IP address of your provisioning host.
2. **(45 Minutes)** From the `data/Packer` directory, run:
   
   ```bash
   PACKER_CACHE_DIR=../../Packer/packer_cache packer build -var-file variables.json windows_10_proxmox.json
   ```

   ```bash
   PACKER_CACHE_DIR=../../Packer/packer_cache packer build -var-file variables.json windows_2016_proxmox.json
   ```

   ```bash
   PACKER_CACHE_DIR=../../Packer/packer_cache packer build -var-file variables.json ubuntu2004_proxmox.json
   ```

   These commands can be run in parallel from three separate terminal sessions.

3. **(1 Minute)** Once the Packer builds finish, verify that you now see Windows10, WindowsServer2016, and Ubuntu2004 templates in your Proxmox console.
4. **(5 Minutes)** In `data/Terraform`, create a `terraform.tfvars` file (RECOMMENDED) to override the default variables listed in `variables.tf`.
5. **(25 Minutes)** From `data/Terraform`, run `terraform init`. The Proxmox Terraform provider should install automatically during this step.
6. Running `terraform apply` should then prompt us to create the logger, dc, wef, and win10 instances. Once finished, you should see the Terraform output with IP addresses of your VMs.
7. Once Terraform has finished bringing the hosts online, change your directory to `data/Ansible`.
8. **(1 Minute)** Edit `data/Ansible/inventory.yml` and replace the IP Addresses with the respective IP Addresses of your Proxmox VMs. At times, the Terraform output is unable to derive the IP address of hosts, so you may have to log into the Proxmox console to find that information and then enter the IP addresses into `inventory.yml`.
9. **(3 Minutes)** Before running any Ansible playbooks, I highly recommend taking snapshots of all your VMs! If anything goes wrong with provisioning, you can simply restore the snapshot and easily debug the issue.
10. **(30 Minutes)** Run `ansible-playbook -v detectionlab.yml`. This will provision the hosts one by one using Ansible. If you’d like to provision each host individually in parallel, you can use `ansible-playbook -v detectionlab.yml –tags “[logger|dc|wef|win10]”` and run each in a separate terminal tab.
11. If all goes well, Ansible will show the Play Recap listing the VM IP addresses without any errors.

### Configuring Windows 10 with WSL as a Provisioning Host [<i class="fas fa-link fa-lg"></i>](https://detectionlab.network/deployment/proxmox/#configuring-windows-10-with-wsl-as-a-provisioning-host)

Note: Run the following commands as a root user or with sudo.

1. In Windows 10, install WSL (version 1 or 2).
2. Install Ubuntu 18.04 app from the Microsoft Store.
3. Update repositories and upgrade the distro: `apt update && upgrade`.
4. Ensure you will install the most recent Ansible version: `apt-add-repository –yes –update ppa:ansible/ansible`.
5. Install the following packages: `apt install python python-pip ansible unzip sshpass libffi-dev libssl-dev`.
6. Install PyWinRM using: `pip install pywinrm`.
7. Install Terraform and Packer by downloading the 64-bit Linux binaries and moving them to `/usr/local/bin`.
8. From `data/Ansible` directory, run: `ansible --version` and ensure that the config file used is `data/Ansible/ansible.cfg`. If not, implement the Ansible “world-writable directory” fix by running: `chmod o-w .` from `data/Ansible` directory.

### Future Work [<i class="fas fa-link fa-lg"></i>](https://detectionlab.network/deployment/proxmox/#future-work)

1. Exchange provisioning is not yet supported.
2. SPICE Support: Implement automated deployment of the SPICE Guest Tools. This will enable automatic screen sizing, copy and paste, and a more enhanced screen experience. At the moment, you can install the SPICE Guest Tools manually in your Windows VMs: [https://www.spice-space.org/download/windows/spice-guest-tools/spice-guest-tools-latest.exe](https://www.spice-space.org/download/windows/spice-guest-tools/spice-guest-tools-latest.exe).