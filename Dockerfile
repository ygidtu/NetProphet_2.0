FROM ubuntu:16.04

# Maintainer: ygidtu <ygidtu@gmail.com>

ENV NETPROPHET2_DIR=/opt/NetProphet_2.0
RUN mkdir $NETPROPHET2_DIR
COPY ./SRC/ $NETPROPHET2_DIR/SRC

# replace 
RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak

COPY sources.list /etc/apt/sources.list

RUN apt-get update && apt-get install -y r-base zlib1g-dev \
    libxml2-dev libxslt-dev \
    autoconf automake \
    libtool elinks \
    unzip wget ruby

# Install python3 requirements
RUN wget -c https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-4.7.12.1-Linux-x86_64.sh
RUN chmod +x Miniconda3-4.7.12.1-Linux-x86_64.sh && ./Miniconda3-4.7.12.1-Linux-x86_64.sh -b -f -p /opt/miniconda3

RUN /opt/miniconda3/bin/pip install -i https://pypi.tuna.tsinghua.edu.cn/simple numpy scipy tqdm

# Install R packages
RUN Rscript -e "install.packages(c('BayesTree', 'lars', 'doMC', 'matrixStats', 'R.oo', 'abind'), repos='https://mirrors.tuna.tsinghua.edu.cn/CRAN/')"

# Install FIRE
WORKDIR $NETPROPHET2_DIR/SRC/
RUN unzip FIRE-1.1a.zip
WORKDIR $NETPROPHET2_DIR/SRC/FIRE-1.1a
RUN chmod +x ./configure
RUN ./configure
RUN make

# Install MEME
RUN ldconfig
WORKDIR $NETPROPHET2_DIR/SRC/
RUN tar -xvzf meme_4.9.1.tar.gz
WORKDIR $NETPROPHET2_DIR/SRC/meme_4.9.1
RUN ./configure --prefix=${NETPROPHET2_DIR}/SRC/meme/ --with-url="http://meme.nbcr.net/meme"
RUN make &&  make install

COPY ./CODE/ $NETPROPHET2_DIR/CODE
COPY main.py $NETPROPHET2_DIR

ENTRYPOINT ["/opt/miniconda3/bin/python3", "/opt/NetProphet_2.0/main.py"]