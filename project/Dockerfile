FROM python:2.7
LABEL maintainer="Thomas Müller"

COPY ./techtrends/ /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN python init_db.py


# command to run on container start
CMD [ "python", "app.py" ]

EXPOSE 3111