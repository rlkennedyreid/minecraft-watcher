FROM python:3.10 as base

# See https://github.com/python-poetry/poetry/discussions/1879#discussioncomment-216865
# for discussion on Poetry + Dockerfile usage and best practices.
ENV \
    PYTHONBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    USERNAME=user \
    PYSETUP_PATH="/opt/pysetup" \
    VIRTUAL_ENV="/opt/pysetup/.venv"

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN useradd --create-home $USERNAME
RUN chown -R $USERNAME:$USERNAME /opt

USER $USERNAME

RUN python -m venv --upgrade-deps $VIRTUAL_ENV

FROM base as builder

USER root

RUN apt-get update --yes --quiet && \
    apt-get --yes --quiet --no-install-recommends install curl && \
    rm -rf /var/lib/apt/lists/*

USER $USERNAME

WORKDIR $PYSETUP_PATH

ENV \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1

ENV PATH="$POETRY_HOME/bin:$PATH"

# https://github.com/python-poetry/poetry/issues/4054
RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.4.0 python - --yes

COPY --chown=$USERNAME:$USERNAME pyproject.toml poetry.lock ./
RUN poetry install --no-dev --no-root

COPY --chown=$USERNAME:$USERNAME README.md ./
COPY --chown=$USERNAME:$USERNAME src ./src

RUN poetry install --no-dev

FROM base as prod

COPY --from=builder $PYSETUP_PATH $PYSETUP_PATH

WORKDIR $PYSETUP_PATH

ENTRYPOINT [ "minecraft-watcher" ]
CMD [ "watch" ]
