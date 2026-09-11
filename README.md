# Ticket Pipeline Demo

This project is a small web app for creating and viewing support
tickets. But the real point of this project isn't the app itself, it's
everything that happens behind the scenes to test it, check it for
security problems, and put it online automatically.

## See it live

https://ticketpipeline-app.whitebay-d7c73885.eastasia.azurecontainerapps.io/health

Note: to save on cloud costs, this may not always be running. If the
link doesn't load, it's just switched off for now, not broken.

## What the app can do

| Action                | What it does               |
| --------------------- | -------------------------- |
| Check if it's running | Visit /health              |
| Create a ticket       | Send a request to /tickets |
| Look up a ticket      | Visit /tickets/(id number) |

Note: tickets are stored in memory only, not a database. Restarting
the container clears them. A production version would add persistent
storage.

## Pipeline overview

Every push to main runs through GitHub Actions:

1. Install dependencies and run the unit test suite
2. Build a Docker image, tagged by commit SHA
3. Push the image to GitHub Container Registry
4. Scan the image with Trivy, high or critical vulnerabilities block the pipeline
5. Promote the scanned image into Azure Container Registry
6. Terraform provisions and updates the live Azure Container App

A vulnerable image cannot reach step 5 or 6, the scan step is an
enforced gate, not just a report.

## Try it on your own computer

    pip install -r requirements.txt
    python app.py

## Run the automatic tests

    python -m pytest tests/ -v

## Run it in a container

    docker build -t ticket-pipeline-demo .
    docker run -p 5000:5000 ticket-pipeline-demo

## How the cloud part works

The cloud setup, servers, storage, networking, is entirely defined in
code, inside the terraform folder. This means the entire online
environment can be deleted and recreated from scratch at any time,
nothing is set up by hand.

## A small intentional detail

Early on, this project was set up with an outdated, insecure software
version on purpose, so the security scan step had something real to
catch and block. It was later updated to a safe version. This is
mentioned here so it's clear it was a deliberate test, not a mistake
that slipped through.
