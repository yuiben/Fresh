FROM python:3.8-buster

# set environment variables
# keeps python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1
# application directory
ENV APP_DIR /app
# set work directory
WORKDIR ${APP_DIR}

# copy project
COPY . .

# expose port
EXPOSE 8000
ENV PORT 8000

# install library
RUN apt-get update && apt-get install -y gettext
RUN python -m pip install --upgrade pip
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry add uvicorn && \
    poetry install --no-dev


CMD ["sh", "-c", "gunicorn device_mngr_auth.wsgi:application -b :8000 --timeout 3600 --threads 4"]