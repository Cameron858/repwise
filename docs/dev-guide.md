# Developer Guide

This project is designed to be started locally with the repository-level Makefile. If you are setting up the app for the first time, start there before running any Docker or database commands manually.

## Prerequisites

- Docker and Docker Compose must be installed and running before you start the app
- Make
- A local `.env` file based on the sample environment file

## 1. Verify Docker is running

Before running any Docker-based setup, confirm that Docker Desktop or the Docker service is installed and actively running on your machine.

## 2. Create your environment file

Copy the sample environment file before starting the stack:

```bash
cp example.env .env
```

Then review the values in `.env` to make sure they match your local setup.

## 3. Use the repository Makefile

The main local workflow is defined in the top-level [Makefile](../Makefile). It wraps the compose commands and aims to keep the developer experience consistent across environments.

Common commands:

```bash
make dev
make down
make restart
```

### What each target does

- `make dev` starts the development stack using the base compose file plus the development override.
- `make down` stops and removes the stack.
- `make restart` stops the stack and starts it again.

## 4. Start the app

From the repository root:

```bash
make dev
```

This will bring up the services defined in the compose configuration using the environment file in the project root.

## 5. Stop or reset the environment

When you want to stop everything:

```bash
make down
```

To fully restart the environment:

```bash
make restart
```

## 6. Troubleshooting

- If containers fail to start, confirm that Docker is running and that `.env` exists and contains valid values.
- If a service is stuck in a bad state, try `make restart`.
- If you need to reset the local environment completely, `make down` removes the stack and related volumes as configured in the project.

For the setup commands, refer to the top-level [Makefile](../Makefile).
