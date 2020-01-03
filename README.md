# NetProphet 2.0 docker image

- [NetProphet 2.0 github](https://github.com/yiming-kang/NetProphet_2.0)
- [current github](https://github.com/ygidtu/NetProphet_2.0)
- [dockerhub](https://hub.docker.com/repository/docker/ygidtu/netprophet2)


## Installation

###  From source

```bash
pip3 install patool

# change patool header from 
# #!/usr/bin/python
# To
# #!/usr/bin/env python3

python3 compres.py

docker build -t {your image name} .
```

### From docker image

```bash
docker pull ygidtu/netprophet2
```

## Original Requirements

- R (>= v3.2, tested on v3.2.1)
- Python (>= v2.7, tested on v2.7.10)
- Python (>= v3.4, tested on 3.4.3+) [Optional, only required for parallel processing]
- Slurm workload manager (tested on v15.08.7)
- Open MPI (tested on v1.8.8)
    - [link](https://download.open-mpi.org/release/open-mpi/v1.8/openmpi-1.8.8.tar.gz)

## New files compare to original repo

- NetProphet_2.0-master-cad8020.zip: is the latest repo of NetProphet (2019-01-03)
- NetProphet2.tar.gz is the package of this repo
- compress.py is a script that used to pack the data i need
- main.py is the entry point of docker image
- SRC/numpy-1.14.0.tar.gz, SRC/scipy-1.2.2.tar.gz is the source code of python numpy and scipy
- SRC/slurm-slurm-15-08-7-1.tar.gz: source code
- SRC/openmpi-1.8.8.tar.gz: source code

## Changes in docker image

- Software version
    - R 3.2.3
    - Python 3.5
    - Python 2.7
        - numpy 1.14.0
        - scipy 1.2.2
    - R 
        - matrixStats
        - R.oo
        - abind
    - Rest using the source code from SRC directory

- Entry point replace the NetProphet2 script with main.py
- Switch the python scripts to using python3 (due to python2 is not longer maintained)

### INSTALLATION INSTRUCTIONS

1.Configure NetProphet 2.0 directory

```bash
export NETPROPHET2_DIR=/path/to/NetProphet_2.0
```

2.Install Snakemake (workflow management system)

```bash
cd ${NETPROPHET2_DIR}/SRC/
tar -zxvf snakemake-3.8.2.tar.gz
cd snakemake-3.8.2/
python3 setup.py build
python3 setup.py install --user
```

3.Install FIRE program

- [tutorial](https://tavazoielab.c2b2.columbia.edu/FIRE/tutorial.html)
- [download page](https://tavazoielab.c2b2.columbia.edu/FIRE/download.php)
- [download link](//tavazoielab.c2b2.columbia.edu/FIRE/download/FIRE-1.1a.zip)

```bash
cd ${NETPROPHET2_DIR}/SRC/
unzip -q FIRE-1.1a.zip
cd FIRE-1.1a/
chmod 775 configure
./configure
make
```

4.Install MEME suite

```bash
cd ${NETPROPHET2_DIR}/SRC/
mkdir -p meme/
tar -zxvf meme_4.9.1.tar.gz
cd meme_4.9.1/
./configure --prefix=${NETPROPHET2_DIR}/SRC/meme --with-url="http://meme.nbcr.net/meme"
make
make test
make install
```

5.Install R packages

- lars v0.9-8
- BayesTree v0.3-1.3
- [optional] Rmpi v0.5-9 (if MPI is available in your system)

```bash
cd ${NETPROPHET2_DIR}/SRC/R_pkgs/
module load R/3.2.1  # SLURM specific, if not loaded by default
R
```

6.Install the following packages:

```R
install.packages("BayesTree_0.3-1.3.tar.gz", lib="<your_local_R_lib>")
install.packages("lars_0.9-8.tar.gz", lib="<your_local_R_lib>")
install.packages("Rmpi_0.5-9.tar.gz", lib="<your_local_R_lib>") # if MPI available
```

7.set variable

```bash
export R_LIBS=/usr/local/lib/R
export PATH=$HOME/.local/bin:$PATH
export PATH=${NETPROPHET2_DIR}:$PATH
export FIREDIR=${NETPROPHET2_DIR}/SRC/FIRE-1.1a/
export PATH=${FIREDIR}:$PATH
export PATH=${NETPROPHET2_DIR}/SRC/meme/bin/:$PATH
```

## Build

```bash
docker build -t ygidtu/netprophet2 .
```
