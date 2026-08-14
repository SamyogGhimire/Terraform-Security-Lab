variable "gce_project" {}
variable "gce_region" {
  default = "europe-west3"
}
variable "gce_machine_type" {
  default = "n1-standard-2"
}
variable "gce_os_image" {
  default = "cos-cloud/cos-stable"
}
variable "gce_ssh_user" {}
variable "gce_ssh_public_key_file" {
  default = "~/.ssh/google_compute_engine.pub"
}
variable "gce_ssh_private_key_file" {
  default = "~/.ssh/google_compute_engine"
}
variable "cluster_name" {
  default = "test"
}
variable "arangodb_password" {}

# Configure the provider
provider "google" {
  project     = "${var.gce_project}"
  region      = "${var.gce_region}"
}

# Allow access from internet to ArangoDB web admin console
resource "google_compute_firewall" "default" {
  name    = "arangodb-graph-rule-cluster"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["8529"]
  }

  target_tags = ["arangodb"]
}

# Create 3 static IP addresses
resource "google_compute_address" "ipa" {
  name = "arangodb-${var.cluster_name}-ipa"
}
resource "google_compute_address" "ipb" {
  name = "arangodb-${var.cluster_name}-ipb"
}
resource "google_compute_address" "ipc" {
  name = "arangodb-${var.cluster_name}-ipc"
}

# Create 3 persistent disks
resource "google_compute_disk" "diska" {
  name = "arangodb-${var.cluster_name}-diska"
  zone = "${var.gce_region}-a"
}
resource "google_compute_disk" "diskb" {
  name = "arangodb-${var.cluster_name}-diskb"
  zone = "${var.gce_region}-b"
}
resource "google_compute_disk" "diskc" {
  name = "arangodb-${var.cluster_name}-diskc"
  zone = "${var.gce_region}-c"
}

# Create 3 hosts - one in each zone a,b & c
resource "google_compute_instance" "hosta" {
  name         = "arangodb-${var.cluster_name}-hosta"
  machine_type = "${var.gce_machine_type}"
  zone         = "${var.gce_region}-a"

  boot_disk {
    initialize_params {
      image = "${var.gce_os_image}"
      size = 10
    }
  }

  attached_disk {
    source = "${google_compute_disk.diska.self_link}"
    device_name = "db"
  }

  network_interface {
    network = "default"
    access_config {
      nat_ip = "${google_compute_address.ipa.address}"
    }
  }

  metadata {
    sshKeys = "${var.gce_ssh_user}:${file(var.gce_ssh_public_key_file)}"
  }

  tags = ["arangodb"]

  # define default connection for remote provisioners
  connection {
    type = "ssh"
    agent = false
    user = "${var.gce_ssh_user}"
    private_key = "${file("${var.gce_ssh_private_key_file}")}"
    timeout = "5m"
  }

  provisioner "file" {
    source      = "scripts/setup.sh"
    destination = "/tmp/setup.sh"
  }

  provisioner "file" {
    source      = "scripts/start.sh"
    destination = "/tmp/start.sh"
  }

  # Mount persistent disk then start master ArangoDBStarter but detatch from terminal
  # otherwise hosta won't finish provisioning and the following hosts need to know it's ip
  provisioner "remote-exec" {
    inline = [
      "chmod +x /tmp/setup.sh",
      "sudo /tmp/setup.sh",
      "chmod +x /tmp/start.sh",
      "/tmp/start.sh ${var.arangodb_password} ${self.network_interface.0.address}",
    ]
  }
}

resource "google_compute_instance" "hostb" {
  name         = "arangodb-${var.cluster_name}-hostb"
  machine_type = "${var.gce_machine_type}"
  zone         = "${var.gce_region}-b"

  boot_disk {
    initialize_params {
      image = "${var.gce_os_image}"
      size = 10
    }
  }

  attached_disk {
    source = "${google_compute_disk.diskb.self_link}"
    device_name = "db"
  }

  network_interface {
    network = "default"
    access_config {
      nat_ip = "${google_compute_address.ipb.address}"
    }
  }

  metadata {
    sshKeys = "${var.gce_ssh_user}:${file(var.gce_ssh_public_key_file)}"
  }

  tags = ["arangodb"]

  # define default connection for remote provisioners
  connection {
    type = "ssh"
    agent = false
    user = "${var.gce_ssh_user}"
    private_key = "${file("${var.gce_ssh_private_key_file}")}"
    timeout = "5m"
  }

  provisioner "file" {
    source      = "scripts/setup.sh"
    destination = "/tmp/setup.sh"
  }

  provisioner "file" {
    source      = "scripts/start.sh"
    destination = "/tmp/start.sh"
  }

  # Start Slave ArangoDB and connect to Master on hosta
  provisioner "remote-exec" {
    inline = [
      "chmod +x /tmp/setup.sh",
      "sudo /tmp/setup.sh",
      "chmod +x /tmp/start.sh",
      "/tmp/start.sh ${var.arangodb_password} ${self.network_interface.0.address} ${google_compute_instance.hosta.network_interface.0.address}"
    ]
  }
}

resource "google_compute_instance" "hostc" {
  name         = "arangodb-${var.cluster_name}-hostc"
  machine_type = "${var.gce_machine_type}"
  zone         = "${var.gce_region}-c"

  boot_disk {
    initialize_params {
      image = "${var.gce_os_image}"
      size = 10
    }
  }

  attached_disk {
    source = "${google_compute_disk.diskc.self_link}"
    device_name = "db"
  }

  network_interface {
    network = "default"
    access_config {
      nat_ip = "${google_compute_address.ipc.address}"
    }
  }

  metadata {
    sshKeys = "${var.gce_ssh_user}:${file(var.gce_ssh_public_key_file)}"
  }

  tags = ["arangodb"]

  # define default connection for remote provisioners
  connection {
    type = "ssh"
    agent = false
    user = "${var.gce_ssh_user}"
    private_key = "${file("${var.gce_ssh_private_key_file}")}"
    timeout = "5m"
  }

  provisioner "file" {
    source      = "scripts/setup.sh"
    destination = "/tmp/setup.sh"
  }

  provisioner "file" {
    source      = "scripts/start.sh"
    destination = "/tmp/start.sh"
  }

  # Start slave ArangoDBstarter and connect to master on hosta
  provisioner "remote-exec" {
    inline = [
      "chmod +x /tmp/setup.sh",
      "sudo /tmp/setup.sh",
      "chmod +x /tmp/start.sh",
      "/tmp/start.sh ${var.arangodb_password} ${self.network_interface.0.address} ${google_compute_instance.hosta.network_interface.0.address}"
    ]
  }
}
