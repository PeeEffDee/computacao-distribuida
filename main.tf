terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>2.65"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~>3.1.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~>2.1.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "default" {
  name     = var.rg
  location = var.location
  tags = {
    environment = "dev"
    source      = "Terraform"
  }
}

resource "tls_private_key" "key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "local_file" "azure_key" {
  filename = "azure_key.pem"
  content  = tls_private_key.key.private_key_pem
}

resource "azurerm_virtual_network" "default" {
  name                = var.vnet
  address_space       = ["10.0.0.0/16"]
  location            = var.location
  resource_group_name = azurerm_resource_group.default.name
}

resource "azurerm_subnet" "internal" {
  name                 = "internal"
  resource_group_name  = azurerm_resource_group.default.name
  virtual_network_name = azurerm_virtual_network.default.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_public_ip" "default" {
  name                = "${var.vm}-pip"
  resource_group_name = azurerm_resource_group.default.name
  location            = var.location
  allocation_method   = "Static"
}

resource "azurerm_network_security_group" "default" {
  name                = "${var.vm}-nsg"
  location            = var.location
  resource_group_name = azurerm_resource_group.default.name

  security_rule {
    name                       = "SSH"
    priority                   = "200"
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_network_interface" "default" {
  name                = "${var.vm}-nic"
  location            = var.location
  resource_group_name = azurerm_resource_group.default.name

  ip_configuration {
    name                          = "${var.vm}-ipconfig"
    subnet_id                     = azurerm_subnet.internal.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.default.id
  }
}

resource "azurerm_network_interface_security_group_association" "default" {
  network_interface_id      = azurerm_network_interface.default.id
  network_security_group_id = azurerm_network_security_group.default.id
}

resource "azurerm_linux_virtual_machine" "main" {
  name                  = var.vm
  location              = var.location
  admin_username        = "azureuser"
  resource_group_name   = azurerm_resource_group.default.name
  network_interface_ids = [azurerm_network_interface.default.id]
  size                  = "Standard_DS1_v2"
  depends_on = [
    azurerm_network_interface_security_group_association.default,
    tls_private_key.key
  ]

  admin_ssh_key {
    username   = "azureuser"
    public_key = tls_private_key.key.public_key_openssh
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "16.04-LTS"
    version   = "latest"
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }
}