#!/usr/bin/env bash

python -m grpc_tools.protoc -Icsi-spec/  --python_out=. --grpc_python_out=. csi-spec/csi.proto
