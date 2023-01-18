# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install apt requirements
RUN apt update -y && apt upgrade -y && \ 
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/* 

# Cloning the repository
RUN git clone https://github.com/YiZaha0/trash-manga-bot /app

# Install pip requirements
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

WORKDIR /app

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["bash", "start.sh"]
