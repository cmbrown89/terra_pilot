FROM terraref/terrautils:1.3
MAINTAINER Max Burnette <mburnet2@illinois.edu>
# Install any programs needed
RUN apt-get update
RUN apt-get install -y python3-pip
RUN pip3 install opencv-python
RUN pip install terraref-stereo-rgb
RUN add-apt-repository ppa:ubuntugis/ubuntugis-unstable \
    && apt-get -q -y update \
    && apt-get install -y gdal-bin libsm6 \
    && rm -rf /var/lib/apt/lists/*
COPY tools /tools
