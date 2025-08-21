# certbot-auth-alidns-hook

A hook program that is designed to be used with `cerbot` CLI.

# Environment Setup

- [AliDNS Python SDK](https://api.aliyun.com/api-tools/sdk/Alidns?version=2015-01-09&language=python-tea&tab=primer-doc) requires Python 3.7 as a minimum.
- This project has `.python-version` set to `3.13.2`, update it as you need.

```
$ pyenv exec python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

# Usage

First, update `run.sh` with your actual Ali Cloud AK.

Then execute: 

```bash
$ certbot certonly \
  --manual \
  --manual-auth-hook /your/absolute/path/to/run.sh \
  --preferred-challenges dns \
  -d xyz.example.com \
  --test-cert
```

> Note:  
> The `--test-cert` uses Lets Encrypt's staging server, you should remove this option after testing. 

Logs will be written to `logs/main.log`, check your AliDNS' TXT record against log messages, ensuring it works as expected.
