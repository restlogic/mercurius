#!/usr/bin/env bash

# SWAGGER_CODEGEN_CLI_JAR_PATH="lib/swagger-codegen-cli-2.4.26.jar"
SWAGGER_CODEGEN_CLI_JAR_PATH="lib/swagger-codegen-cli-3.0.36.jar"

for f in swagger-spec/*.yaml
do
    k=$(echo ${f} | sed -r 's;swagger-spec/(.+);\1;')
    echo k=${k}
    echo f=${f}
    python3 preprocess_pkl.py --out-file prefix-summary-agg-groups/${k}.pkl --key ${k}
    java -jar "${SWAGGER_CODEGEN_CLI_JAR_PATH}" generate -i swagger-spec/${k} -l python -o swagger-clients/${k}
    cd swagger-clients/${k}
    python3 setup.py sdist
    cd ../..
    # docker run --rm -v `pwd`/swagger-spec/${k}:/opt/work/provide/nova.yaml -v `pwd`/prefix-summary-agg-groups/${k}.pkl:/opt/work/provide/prefix-summary-agg-group.pkl ifdt/swagger-default-parameter:v1 > swagger-default-parameters/${k}.py
done