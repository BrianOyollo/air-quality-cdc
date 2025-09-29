FROM python:3.13-slim


# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app

COPY ./pyproject.toml ./uv.lock ./.python-version /app/
COPY ./src/app /app/src/app


# Sync the project into a new environment, asserting the lockfile is up to date
RUN uv sync --locked
