#FROM ubuntu:xenial
FROM python:3.7-slim-buster

# Install utilities
# TODO: what all do we really need here? test with none and add incrementally
#RUN apt-get update && apt-get install -y \
#    python3 python3-pip
#    unzip xorg wget libxml2-dev libxslt1-dev git libfreetype6-dev \
#    zlib1g-dev pkg-config \
#    python-pip python-dev python-requests

RUN apt-get update && apt-get install -y git

RUN python --version
RUN pip --version
RUN pip install pip --upgrade

# Install dax
RUN pip install git+https://github.com/VUIIS/dax.git@rc1 --upgrade

# TODO: test a dax command here

# Install dcm2niix
RUN pip install nibabel
RUN apt-get install -y cmake g++
RUN mkdir dcm2niix && \
	cd dcm2niix && \
	git clone https://github.com/neurolabusc/dcm2niix.git DCM2NIIX && \
	mkdir build && \
	cd build && \
	cmake -DCMAKE_BUILD_TYPE=Release \
		../DCM2NIIX && \
	make && \
	make install && \
	cd ../.. && \
	rm -rf dcm2niix

# Install dax modules, processors, and pipelines
# pip install dax-pipelines
# for now we'll copy them in from local zip
#COPY dax-pipelines-master.zip /opt/
#RUN unzip -q /opt/dax-pipelines-master.zip -d /opt && \
#	rm -r /opt/dax-pipelines-master.zip

# usage: run settings.py daxnetrc [email] steps
# e.g run ~/settings.py ~/.daxnetrc --steps build+upload
# # e.g run ~/settings.py ~/.daxnetrc --steps update,launch
# plus indicates parallel, comma indicates serial
# ^this  isn't quite right yet

COPY run.sh /opt/
RUN chmod +x /opt/run.sh
ENTRYPOINT ["/opt/run.sh"]

#ENTRYPOINT ["/bin/bash"]
