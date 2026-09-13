# Deploy Runbook

Steps to bring this project's infrastructure back online after a
teardown, and how to handle the issues that came up the first few times.

## Standard redeploy, in order

**1. Recreate the infrastructure**

    cd terraform
    terraform apply

Type `yes` when prompted. This recreates the resource group, ACR,
environment, and container app, in that order. The container app step
will likely fail here, that is expected, see below.

**2. Get a real image into the freshly created ACR**

A fresh ACR has no images in it, so the container app cannot start yet.
Push any commit (or trigger the workflow manually) so the full pipeline
runs and the `promote-image` job imports a real image:

    git commit --allow-empty -m "chore: trigger pipeline to promote image"
    git push

Confirm the image actually landed:

    az acr repository show-tags --name ticketpipelineacr --repository ticket-pipeline-demo --output table

**3. Check the AZURE_CREDENTIALS secret before assuming anything is broken**

If `promote-image` fails with a login or "no subscriptions found" error,
check whether the secret is actually populated:

GitHub repo -> Settings -> Secrets and variables -> Actions ->
AZURE_CREDENTIALS

If it looks wrong or was possibly saved empty, regenerate it:

    az ad sp create-for-rbac --name "ticketpipeline-github-actions" --role contributor --scopes /subscriptions/<subscription-id>/resourceGroups/ticketpipeline-rg --sdk-auth

Copy the full JSON output, paste it into the secret's value field, save,
then re-run the failed job from the Actions tab, do not assume a push
is needed if only the secret changed.

**4. Finish provisioning the container app**

Once a real image exists in ACR:

    cd terraform
    terraform apply

If this fails with "A resource already exists", the app was partially
created in an earlier failed attempt. Import it into state, then apply
again:

    terraform import azurerm_container_app.main /subscriptions/<subscription-id>/resourceGroups/ticketpipeline-rg/providers/Microsoft.App/containerApps/ticketpipeline-app
    terraform apply

If apply reports success but the container still fails to pull the
image ("not found in the registry") even though the image genuinely
exists in ACR, this is a known issue, Terraform's in place update can
reuse a stale ACR password reference. Force a full recreate instead of
an in place update:

    terraform apply -replace="azurerm_container_app.main"

**5. Get the live URL and update the README**

    az containerapp show --name ticketpipeline-app --resource-group ticketpipeline-rg --query properties.configuration.ingress.fqdn --output tsv

This domain is randomly generated and will be different every time the
environment is recreated from scratch. Update the live demo link in
README.md with the new URL before considering the redeploy done.

## Tearing down

    cd terraform
    terraform destroy

This removes everything, including ACR and its images. The next
redeploy will need to go through the full sequence above again,
including re-promoting an image, since a fresh ACR starts empty.

## Known gotchas, summarized

- A fresh base image pull does not guarantee patched OS packages, the
  Dockerfile runs `apt-get upgrade` during build specifically to avoid
  waiting on Docker Hub's rebuild schedule for security patches
- Destroying the resource group also deletes any role assignment scoped
  to it, the service principal's access must be recreated after every
  full teardown, not just its secret rotated
- Container app "image not found" errors can mean the image is
  genuinely missing, or that ACR credentials are stale, check the image
  actually exists in ACR before assuming either cause
- The live URL changes every time the environment is recreated, this
  is expected, not a bug
