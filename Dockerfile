FROM python:3.10-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    postgresql-client \
    git \
    && rm -rf /var/lib/apt/lists/*

# Installer Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

ENV PATH="/root/.local/bin:$PATH"

# Copier fichiers de configuration Poetry
COPY pyproject.toml poetry.lock ./

# Installer les dépendances (sans le projet lui-même)
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only main --no-interaction --no-ansi

# Copier le code source
COPY . .

# Rendre le script entrypoint exécutable
RUN chmod +x /app/entrypoint.sh

# Exposer le port
EXPOSE 8000

# Utiliser le script d'initialisation
ENTRYPOINT ["/app/entrypoint.sh"]
