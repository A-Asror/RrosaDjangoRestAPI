FROM python:3.9.16

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

RUN apt-get update -y \
    && apt-get install -y libffi-dev gcc python3-dev musl-dev g++ postgis ffmpeg vim
#    postgresql nano
#    && apk add binutils python-gdal \ zlib-dev py-pip
#    && apk add postgresql-dev
#    && gdal-bin binutils libproj-dev libgdal-dev
#    && libgdal-dev binutils libproj-dev python3-gdal gdal-bin
# musl-dev jpeg-dev apk add libressl-dev perl rust libmagic pango openjpeg-dev


# Upgrade pip
RUN pip install --upgrade pip

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/backend
ENV LOCAL_APP=././././
RUN mkdir $HOME
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/static
RUN mkdir $APP_HOME/media
RUN mkdir $APP_HOME/logs

# set work directory
WORKDIR $APP_HOME

# Install dependencies
COPY ./requirements $APP_HOME/requirements
RUN pip install -r requirements/dev.txt

# copy project
COPY $LOCAL_APP $APP_HOME

# create the app user
# RUN groupadd -r www-data && useradd -r -g www-data www-data
# RUN addgroup -S www-data && adduser  -S app -G app alpine

# chown all the files to the www-data user
#RUN chown -R www-data:www-data $APP_HOME/media
RUN chown -R www-data:www-data $APP_HOME

#ARG USER=www-data
#USER $USER


# run entrypoint.prod.sh
RUN ["chmod", "+x", "/home/app/backend/.docker/dev/backend/entrypoint.sh"]
ENTRYPOINT ["/home/app/backend/.docker/dev/backend/entrypoint.sh"]
