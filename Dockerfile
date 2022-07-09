FROM python:3.9.13-slim-buster as production

WORKDIR /app

# Additional packages to help debug - slim-buster is very streamlined ...
RUN apt-get update && apt-get install -y procps  && apt-get install -y vim && apt-get install -y curl
# RUN apt-get install -y build-essential

RUN useradd -m sid
RUN chown -R sid:sid /app
USER sid
ENV PATH="/home/sid/.local/bin:${PATH}"

COPY requirements requirements
RUN pip install --upgrade pip
RUN pip install --no-cache --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org  --user -r requirements/prod.txt

COPY logging.conf logging.conf
COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY supervisord_programs /etc/supervisor/conf.d
COPY shell_scripts shell_scripts

COPY *.py ./

COPY unido_printing_service unido_printing_service

# DataDog Stuff
ARG GIT_REVISION
ARG FULL_VERSION
ARG PACKAGE_NAME

LABEL com.datadoghq.tags.service=$PACKAGE_NAME
LABEL com.datadoghq.tags.version=$FULL_VERSION
ENV DD_SERVICE $PACKAGE_NAME
ENV DD_VERSION $FULL_VERSION

EXPOSE 7095
ENTRYPOINT ["/bin/bash", "shell_scripts/supervisord_entrypoint.sh"]
CMD ["-c", "/etc/supervisor/supervisord.conf"]
