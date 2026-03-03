#!/bin/bash
# Foldseek
# If you get an init error uncomment the below (worked on 2 clusters and borked the conda install on the third..)
# CONDA_BASE=$(conda info --base)
# source $CONDA_BASE/etc/profile.d/conda.sh
conda activate enzymetk
conda install -c conda-forge -c bioconda foldseek -y
conda install -c conda-forge -c bioconda mmseqs2 -y