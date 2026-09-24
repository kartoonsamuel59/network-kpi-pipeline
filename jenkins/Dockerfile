FROM jenkins/jenkins:lts-jdk17

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        awscli \
        python3 \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-27.3.1.tgz -o /tmp/docker.tgz \
    && tar xzvf /tmp/docker.tgz --strip-components=1 -C /usr/local/bin docker/docker \
    && chmod +x /usr/local/bin/docker \
    && rm /tmp/docker.tgz

COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

USER jenkins