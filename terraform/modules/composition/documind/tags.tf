locals {
  base_tags = {
    Environment = var.environment
    ProjectName = var.project_name
    Owner       = var.owner_email
    CostCenter  = var.cost_center
    ManagedBy   = "Terraform"
  }

  security_tags = {
    DataClassification = "Restricted"
    ContainsSecrets    = "True"
    ComplianceScope    = "None"
    PII                = "False"
  }
}
