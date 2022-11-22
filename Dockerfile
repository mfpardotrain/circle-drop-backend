FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN pip install -r requirements.txt
EXPOSE 8000
CMD python /code/circle-drop-backend/manage.py runserver 0.0.0.0:8000
