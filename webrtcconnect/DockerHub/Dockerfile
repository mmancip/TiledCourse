FROM tileubuntu

ENV NGINX_VERSION nginx-1.18.0
ENV NGINX_RTMP_MODULE_VERSION 1.2.1

ENV DEBIAN_FRONTEND noninteractive
# TYPE is used for start.sh script

ENV DOCKER_PATH "."


# Install and clean
RUN apt-get update \
    && apt-get install -y \
	pulseaudio \
	openssh-server \
	ca-certificates \
	openssl \
	libssl-dev libpcre3 libpcre3-dev zlib1g zlib1g-dev\
	make gcc 	

RUN apt-get autoclean \
    && apt-get clean
RUN rm -rf /var/lib/apt/lists/*

# https://hub.docker.com/r/tiangolo/nginx-rtmp/
# Download and decompress Nginx
RUN mkdir -p /tmp/build/nginx && \
    cd /tmp/build/nginx && \
    wget -O ${NGINX_VERSION}.tar.gz https://nginx.org/download/${NGINX_VERSION}.tar.gz && \
    tar -zxf ${NGINX_VERSION}.tar.gz

# Download and decompress RTMP module
RUN mkdir -p /tmp/build/nginx-rtmp-module && \
    cd /tmp/build/nginx-rtmp-module && \
    wget -O nginx-rtmp-module-${NGINX_RTMP_MODULE_VERSION}.tar.gz https://github.com/arut/nginx-rtmp-module/archive/v${NGINX_RTMP_MODULE_VERSION}.tar.gz && \
    tar -zxf nginx-rtmp-module-${NGINX_RTMP_MODULE_VERSION}.tar.gz && \
    cd nginx-rtmp-module-${NGINX_RTMP_MODULE_VERSION}

# Build and install Nginx
# The default puts everything under /usr/local/nginx, so it's needed to change
# it explicitly. Not just for order but to have it in the PATH
RUN cd /tmp/build/nginx/${NGINX_VERSION} && \
    ./configure \
        --sbin-path=/usr/local/sbin/nginx \
        --conf-path=/etc/nginx/nginx.conf \
        --error-log-path=/var/log/nginx/error.log \
        --pid-path=/var/run/nginx/nginx.pid \
        --lock-path=/var/lock/nginx/nginx.lock \
        --http-log-path=/var/log/nginx/access.log \
        --http-client-body-temp-path=/tmp/nginx-client-body \
        --with-http_ssl_module \
        --with-threads \
        --with-ipv6 \
        --add-module=/tmp/build/nginx-rtmp-module/nginx-rtmp-module-${NGINX_RTMP_MODULE_VERSION} && \
    make -j $(getconf _NPROCESSORS_ONLN) && \
    make install && \
    mkdir /var/lock/nginx && \
    rm -rf /tmp/build


RUN mkdir /var/run/sshd


# Configure nginx
COPY $DOCKER_PATH/build_files/nginx.conf /etc/nginx/nginx.conf
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log


# Configure user myuser
RUN mkdir -p /home/myuser
#RUN adduser --disabled-password --gecos "My User" --uid 1000 myuser


ENV ID_CLASSROOM -1
ENV JITSI_SERVER -1
ENV VIDEO_DEVICE -1
ENV TEACHER_NAME -1
ENV TEACHER_EMAIL -1


COPY $DOCKER_PATH/build_files/ssh/id_rsa_hub.pub /home/myuser/.ssh/authorized_keys
COPY $DOCKER_PATH/build_files/ssh/id_rsa_hub*  /home/myuser/.ssh/

# Start
RUN rm -f /start.sh
COPY $DOCKER_PATH/start.sh /start.sh
COPY $DOCKER_PATH/build_files/start.sh /opt/start-hub.sh
COPY $DOCKER_PATH/build_files/launch_sound.sh /opt/launch_sound.sh

EXPOSE 22
EXPOSE 1935


CMD ["-r","800x600","-u","1000","-g","1000","-p","55555","-h","localhost"]
