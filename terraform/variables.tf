variable "project_name" {
  description = "Short name used as a prefix for all resources"
  type        = string
  default     = "ticketpipeline"
}

variable "location" {
  description = "Azure region resources are created in"
  type        = string
  default     = "eastasia"
}