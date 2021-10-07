FROM python:3.9.7

ARG project_dir=/projects/

ADD ./requirements.txt $project_dir

WORKDIR $project_dir

RUN pip install -r requirements.txt

RUN apt update && apt install -y openjdk-11-jdk curl

EXPOSE 8000

CMD ["gunicorn", "ash_unofficial_covid19.run:app", "-b", "0.0.0.0:8000"]
