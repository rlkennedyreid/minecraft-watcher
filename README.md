# minecraft-watcher
A poetry CLI tool that 'watches' a Minecraft server,
and sends a `POST` request to a given webhook when the server has been empty for a given period of time.

## Requirements

### Simple usage
  - [Python](https://www.python.org/)
    - [pyenv](https://github.com/pyenv/pyenv) is recommended for managing your python versions
  - [Poetry](https://python-poetry.org/docs/#installation)

### Development
  - [pre-commit](https://pre-commit.com/#install)

## Installation

To install dev and prod dependencies as well as the root package, run

```shell
poetry install
```

## Usage

### Configuration

The tool is configured using environment variables.
These can be exported to your shell environment,
or saved to a file in your working directory called `.env`.

[`.env.example`](./.env.example) gives the available configuration
variables for the tool.

## Running
After installing the package and configuring, simply run

```shell
minecraft-watcher watch
```

The tool will then poll `HOST:PORT` every `TIMEOUT_S` seconds.
After 2 consecutive polls indicate the server has no players connected,
a `POST` request will be sent to `KILL_WEBHOOK` and the tool quits.

If the tool cannot obtain info from `HOST:PORT`,
it will retry forever; approximately every 10 seconds.

If `POST` request to `KILL_WEBHOOK` receives an error response,
it will be retried 5 times, then quit.

## Docker container

A [Dockerfile](./Dockerfile) and accompanying [compose file](./docker-compose.yml) are provided,
which install the tool and run it on startup automatically.

**NOTE:** The environment variables still need to be provided to the compose stack.
See [here](https://docs.docker.com/compose/environment-variables/set-environment-variables).

## Extra info
`KILL_WEBHOOK` could be any URL.
The intended purpose of this tool is to automatically shutdown my Minecraft server
VM(s) when the servers are not in use.

I'm using Microsoft Azure for my Minecraft server,
so the webhook I am using [starts a runbook](https://learn.microsoft.com/en-us/azure/automation/automation-webhooks)
that can spin up the VM.
I use another webhook to start up the VM, but that is irrelevant to this tool.

The runbook I am using is shown in [`vm-control-script.ps1`](./vm-control-script.ps1).
