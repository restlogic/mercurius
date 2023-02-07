#!/usr/bin/env bash

cd $(dirname -- "$0")

rm prefix-summary-agg-group.pkl
rm -rf prefix-summary-agg-groups
rm -rf swagger-clients
rm -rf swagger-spec

mkdir -p prefix-summary-agg-groups
mkdir -p swagger-clients

cp -r ../juno/swagger-spec ./
cp ../juno/prefix-summary-agg-group.pkl ./
./run.sh

