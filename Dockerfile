# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim

EXPOSE 10102

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /tenderflowapi

# Copy the current app directory contents into the container at /app
COPY ./app /tenderflowapi/app
COPY ./requirements.txt /tenderflowapi/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r /tenderflowapi/requirements.txt

# Make port 10101 available to the world outside this container
EXPOSE 10102

# add PYTHONPATH to solve absolute import error for docker
ENV PYTHONPATH "${PYTHONPATH}:/tenderflowapi/app"

###############################
# Creates a non-root user with an explicit UID and adds permission to access the /tenderflowapi folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /tenderflowapi
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
#CMD ["gunicorn", "--bind", "0.0.0.0:10102", "-k", "uvicorn.workers.UvicornWorker", "app.main:app"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10102"]
