#!/usr/bin/env bash

echo "${1}"
echo "Continue? [y]"
read

pip uninstall -y swagger_client
pip install swagger-clients/${1}/dist/swagger-client-1.0.0.tar.gz
python main.py -d --prefix-summary-agg-group-pkl-path prefix-summary-agg-groups/${1}.pkl 2> results/${1}.log
pip uninstall -y swagger_client