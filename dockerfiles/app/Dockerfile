FROM python:3.11.6

RUN pip install --upgrade pip

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

RUN curl -sSL https://install.python-poetry.org | python -

RUN mkdir /var/gunicorn

RUN chmod 777 /var/gunicorn

ARG project_dir=/projects/

ADD ./pyproject.toml $project_dir

WORKDIR $project_dir

RUN apt-get update && apt-get install -y default-jdk curl libgl1-mesa-dev ghostscript

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN poetry update

CMD ["poetry", "run", "gunicorn", "ash_unofficial_covid19.run:app", "-c", "gunicorn.conf.py"]
