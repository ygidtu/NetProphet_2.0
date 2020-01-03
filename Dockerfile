FROM ubuntu:16.04

# Maintainer: ygidtu <ygidtu@gmail.com>

ENV NETPROPHET2_DIR=/opt/NetProphet_2.0

RUN mkdir $NETPROPHET2_DIR
COPY NetProphet2.tar.gz $NETPROPHET2_DIR

WORKDIR $NETPROPHET2_DIR
RUN tar -xvzf NetProphet2.tar.gz

# replace 
RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak
COPY sources.list /etc/apt/sources.list
COPY Rprofile ~/.Rprofiler

RUN apt-get update && apt-get install -y python-pip python3 python3-pip r-base zlib1g-dev libxml2-dev libxslt-dev autoconf automake libtool elinks unzip

# Decompress data
WORKDIR $NETPROPHET2_DIR/SRC
RUN for i in $(ls *.tar.gz); do tar -xvzf $i; done

# Install slurm
WORKDIR $NETPROPHET2_DIR/SRC/slurm-slurm-15-08-7-1
RUN ./configure
RUN make && make install

# Install openmpi
WORKDIR $NETPROPHET2_DIR/SRC/openmpi-1.8.8
RUN ./configure
RUN make && make install

# Install FIRE
WORKDIR $NETPROPHET2_DIR/SRC/
RUN unzip FIRE-1.1a.zip
WORKDIR $NETPROPHET2_DIR/SRC/FIRE-1.1a
RUN chmod +x ./configure
RUN ./configure
RUN make

# Install MEME
RUN ldconfig
WORKDIR $NETPROPHET2_DIR/SRC/meme_4.9.1
RUN ./configure --prefix=${NETPROPHET2_DIR}/SRC/meme/ --with-url="http://meme.nbcr.net/meme"
RUN make &&  make install

# Install snakemake
WORKDIR $NETPROPHET2_DIR/SRC/snakemake-3.8.2
RUN python3 setup.py install

WORKDIR $NETPROPHET2_DIR/SRC/numpy-1.14.0
RUN python2 setup.py install

WORKDIR $NETPROPHET2_DIR/SRC/scipy-1.2.2
RUN python2 setup.py install

# Install R packages
RUN R CMD INSTALL ../R_pkgs/BayesTree_0.3-1.3.tar.gz
RUN R CMD INSTALL ../R_pkgs/lars_0.9-8.tar.gz
RUN R CMD INSTALL ../R_pkgs/Rmpi_0.5-9.tar.gz
RUN Rscript -e "install.packages('matrixStats', repos = 'https://mirrors.tuna.tsinghua.edu.cn/CRAN/')"
RUN Rscript -e "install.packages('R.oo', repos = 'https://mirrors.tuna.tsinghua.edu.cn/CRAN/')"
RUN Rscript -e "install.packages('abind', repos = 'https://mirrors.tuna.tsinghua.edu.cn/CRAN/')"

# Set variable
ENV NETPROPHET2_DIR=/opt/NetProphet_2.0
ENV R_LIBS=/usr/local/lib/R
ENV FIREDIR=${NETPROPHET2_DIR}/SRC/FIRE-1.1a/
ENV PATH=$HOME/.local/bin:${NETPROPHET2_DIR}:${FIREDIR}:${NETPROPHET2_DIR}/SRC/meme/bin/:$PATH

RUN export NETPROPHET2_DIR=/opt/NetProphet_2.0 >> ~/.bashrc
RUN export R_LIBS=/usr/local/lib/R >> ~/.bashrc
RUN export FIREDIR=${NETPROPHET2_DIR}/SRC/FIRE-1.1a/ >> ~/.bashrc
RUN export PATH=$HOME/.local/bin:${NETPROPHET2_DIR}:${FIREDIR}:${NETPROPHET2_DIR}/SRC/meme/bin/:$PATH >> ~/.bashrc

ENTRYPOINT ["python3", "/opt/NetProphet_2.0/main.py"]