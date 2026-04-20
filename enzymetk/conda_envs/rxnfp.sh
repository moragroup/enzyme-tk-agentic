#!/bin/bash

conda create -n rxnfp --channel conda-forge python=3.10 pip -y
# Had issues with this on the AITHYRA server so removing it for now
#CONDA_BASE=$(conda info --base)
#source $CONDA_BASE/etc/profile.d/conda.sh

conda activate rxnfp
conda install -c rdkit rdkit=2020.03.3 -y
conda install -c tmap tmap -y
pip install rxnfp
pip install numpy==1.23
pip install rdkit
pip install sciutil
pip install torch --index-url https://download.pytorch.org/whl/cu130
pip install enzymetk
pip install transformers==4.30 