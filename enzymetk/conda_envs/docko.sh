#!/bin/bash
# Docko
conda  create --name docko python=3.10.14 pip -y
conda activate docko
conda config --env --add channels conda-forge
conda install -c conda-forge pdbfixer -y
pip install git+https://github.com/chaidiscovery/chai-lab.git
pip install docko
pip install cuequivariance
pip install cuequivariance-torch
pip install cuequivariance-ops-torch-cu13 # or whichever one you need for your cuda version
pip install --upgrade click
pip install enzymetk