# Use nvidia/cuda image
FROM nvidia/cuda:11.2.1-base-ubuntu20.04


ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
RUN apt-get update

RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*

RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh 
RUN conda --version

RUN mkdir app
WORKDIR app
RUN apt update
RUN apt install -y git



WORKDIR /app

# Install dependencies:
COPY requirements.txt .
# Install dependencies:
COPY environment.yaml .

RUN conda env create -f ./environment.yaml
RUN echo "source activate algocean" > ~/.bashrc
ENV PATH /opt/conda/envs/algocean/bin:$PATH
RUN /bin/bash -c "source activate algocean"
RUN apt install -y gcc
RUN /bin/bash -c "pip install -r requirements.txt"

ADD ./ocean.py /app/ocean.py
RUN /bin/bash -c "pip install -e ./ocean.py"
ADD ./ipfspy /app/ipfspy
RUN /bin/bash -c "pip install -e ./ipfspy"

ADD ./ipfsspec /app/ipfsspec
RUN /bin/bash -c "pip install -e ./ipfsspec"
RUN /bin/bash -c "pip install hub"


# RUN conda activate algocean
# add BITTENSOR commune fork


