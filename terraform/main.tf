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