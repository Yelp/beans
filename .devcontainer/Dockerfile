ARG VARIANT="jammy"
FROM mcr.microsoft.com/vscode/devcontainers/base:0-${VARIANT}

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
        | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
        && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - \
        && apt-get update && export DEBIAN_FRONTEND=noninteractive \
        && apt-get -y install --no-install-recommends fish google-cloud-cli vim
