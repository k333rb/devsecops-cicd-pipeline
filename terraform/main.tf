# Groups every resource this project creates under one deletable unit,
# running terraform destroy removes everything at once when not demoing
resource "azurerm_resource_group" "main" {
  name     = "${var.project_name}-rg"
  location = var.location
}

# Basic tier keeps cost minimal, sufficient for a small demo image
resource "azurerm_container_registry" "main" {
  name                = "${var.project_name}acr"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true
}

resource "azurerm_container_app_environment" "main" {
  name                = "${var.project_name}-env"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
}

resource "azurerm_container_app" "main" {
  name                         = "${var.project_name}-app"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  # Scales to zero when idle, avoids paying for compute with no traffic
  template {
    min_replicas = 0
    max_replicas = 1

    container {
      name   = "ticket-api"
      image  = "${azurerm_container_registry.main.login_server}/ticket-pipeline-demo:latest"
      cpu    = 0.25
      memory = "0.5Gi"
    }
  }

  # Lets the app pull private images from ACR using its admin credentials
  registry {
    server               = azurerm_container_registry.main.login_server
    username              = azurerm_container_registry.main.admin_username
    password_secret_name  = "acr-password"
  }

  secret {
    name  = "acr-password"
    value = azurerm_container_registry.main.admin_password
  }

  ingress {
    external_enabled = true
    target_port       = 5000
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }
}
