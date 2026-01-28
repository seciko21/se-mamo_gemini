FROM alpine:latest

# Instalar cliente SSH
RUN apk add --no-network --no-cache openssh-client

# Copiar tus llaves SSH (las que acabamos de arreglar) al contenedor
RUN mkdir -p /root/.ssh
COPY /root/.ssh/id_rsa /root/.ssh/id_rsa

# Ajustar permisos estrictos para SSH
RUN chmod 700 /root/.ssh && chmod 600 /root/.ssh/id_rsa

# Comando para iniciar el túnel con reconexión automática
# -o ExitOnForwardFailure=yes permite que el contenedor falle si el túnel cae, 
# para que Docker lo reinicie.
ENTRYPOINT ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ServerAliveInterval=30", "-o", "ExitOnForwardFailure=yes", "-R", "80:radar_dashboard:8501", "localhost.run"]
