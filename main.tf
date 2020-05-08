provider "aws" {
  version = "1.39"
  region  = "${var.region}"

  assume_role {
    role_arn = "${var.role_arn}"
  }
}

data "terraform_remote_state" "env_remote_state" {
  backend   = "s3"
  workspace = "${terraform.workspace}"

  config {
    bucket   = "${var.alm_state_bucket_name}"
    key      = "operating-system"
    region   = "us-east-2"
    role_arn = "${var.alm_role_arn}"
  }
}

resource "local_file" "kubeconfig" {
  filename = "${path.module}/outputs/kubeconfig"
  content = "${data.terraform_remote_state.env_remote_state.eks_cluster_kubeconfig}"
}

data "aws_secretsmanager_secret_version" "data_science_db_password" {
  secret_id = "${data.terraform_remote_state.env_remote_state.data_science_db_secret_id}"
}

resource "local_file" "helm_vars" {
  filename = "${path.module}/outputs/${terraform.workspace}.yaml"
  content = <<EOF
mssql:
  username: "${data.terraform_remote_state.env_remote_state.data_science_db_username}"
  server: "${data.terraform_remote_state.env_remote_state.data_science_db_server}"
  password: "${data.aws_secretsmanager_secret_version.data_science_db_password.secret_string}"
EOF
}

resource "null_resource" "helm_deploy" {
  provisioner "local-exec" {
    command = <<EOF
set -x

export KUBECONFIG=${local_file.kubeconfig.filename}

export AWS_DEFAULT_REGION=us-east-2
helm upgrade --install predictive-parking-etl ./chart --namespace=predictive-parking \
    --values ${local_file.helm_vars.filename} \
    ${var.extra_helm_args}
EOF
  }

  triggers {
    # Triggers a list of values that, when changed, will cause the resource to be recreated
    # ${uuid()} will always be different thus always executing above local-exec
    hack_that_always_forces_null_resources_to_execute = "${uuid()}"
  }
}

variable "extra_helm_args" {
  description = "Helm options"
  default     = ""
}

variable "is_internal" {
  description = "Should the ALBs be internal facing"
  default     = false
}

variable "region" {
  description = "Region of ALM resources"
  default     = "us-west-2"
}

variable "role_arn" {
  description = "The ARN for the assume role for ALM access"
  default     = "arn:aws:iam::199837183662:role/jenkins_role"
}

variable "alm_role_arn" {
  description = "The ARN for the assume role for ALM access"
  default     = "arn:aws:iam::199837183662:role/jenkins_role"
}

variable "alm_state_bucket_name" {
  description = "The name of the S3 state bucket for ALM"
  default     = "scos-alm-terraform-state"
}

variable "alm_workspace" {
  description = "The workspace to pull ALM outputs from"
  default     = "alm"
}

