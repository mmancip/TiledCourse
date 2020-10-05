FROM mageianvidia:7

MAINTAINER  "Martial Mancip" <Martial.Mancip@MaisondelaSimulation.fr>

#RUN urpmi -y lib64gom1.0_0 pulseaudio-12.2-5

RUN urpmi.update -a && \
    urpmq lib64nss3 lib64nspr4 lib64vulkan-loader1 && \
    urpmi -y lib64nss3 lib64nspr4 lib64vulkan-loader1

RUN urpmi -y at-3.1.23

RUN atd &
    
RUN urpmi.addmedia Google\ Chrome\ 64bit http://dl.google.com/linux/chrome/rpm/stable/x86_64 && \
    urpmi -y --force  google-chrome-stable 

RUN urpmi ffmpeg

COPY command_chrome /opt
COPY command_ffmpeg /opt
