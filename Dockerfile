FROM terraref/terrautils:1.5
LABEL maintainer="Chris Schnaufer <schnaufer@email.arizona.edu>"

RUN useradd -u 49044 extractor \
    && mkdir /home/extractor \
    && mkdir /home/extractor/sites

RUN chown -R extractor /home/extractor \
    && chgrp -R extractor /home/extractor 

RUN apt-get update

RUN apt-get install libgdal-dev \
        python-gdal \
        python-tk

RUN pip install --upgrade pip 

RUN pip install -U numpy && \
    pip install -U pyclowder && \
    pip install -U laspy && \
    pip install gdal  && \
    pip install terraref_stereo_rgb && \
    pip install terrautils

# command to run when starting docker
COPY bin2tif.py /home/extractor/
COPY sensors /home/extractor/sensors
RUN chmod +x /home/extractor/bin2tif.py

WORKDIR /home/extractor
ENTRYPOINT ["/home/extractor/bin2tif.py"]
CMD ["", "", ""]
