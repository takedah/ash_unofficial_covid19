FROM python:3.9.7

RUN mkdir /var/gunicorn

RUN chmod 777 /var/gunicorn

ARG project_dir=/projects/

ADD ./requirements.txt $project_dir

WORKDIR $project_dir

RUN pip install -r requirements.txt

RUN apt update && apt install -y openjdk-11-jdk curl libgl1-mesa-dev ghostscript

CMD ["gunicorn", "ash_unofficial_covid19.run:app", "-c", "gunicorn.conf.py"]
