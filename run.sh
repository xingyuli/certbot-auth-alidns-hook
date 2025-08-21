#!/bin/bash
export ALIBABA_CLOUD_ACCESS_KEY_ID=your-ak-id
export ALIBABA_CLOUD_ACCESS_KEY_SECRET=your-ak-secret

script_dir=`cd $(dirname $0) && pwd`
cd $script_dir

source .venv/bin/activate
python main.py
