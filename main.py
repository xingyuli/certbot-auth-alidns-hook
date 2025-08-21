import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from alibabacloud_alidns20150109.client import Client
from alibabacloud_alidns20150109 import models
from alibabacloud_tea_openapi import models as open_api_models


config = open_api_models.Config(
    access_key_id=os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'],
    access_key_secret=os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'],
)
config.endpoint = 'alidns.cn-hangzhou.aliyuncs.com'


_global_logger = None

def init_logger(entry_name):
    """
    Initializes the global logger. Should be called once by the main script.
    """
    global _global_logger
    if _global_logger:
        # This can be a warning or a silent return if re-initialization is okay
        return _global_logger

    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configure the root logger
    _global_logger = logging.getLogger()
    _global_logger.setLevel(logging.DEBUG)

    handler = RotatingFileHandler(
        os.path.join(log_dir, f"{entry_name}.log"),
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    formatter = logging.Formatter('%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Create a stream handler for stdout
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(formatter)

    # Clear existing handlers and add the new ones
    if _global_logger.hasHandlers():
        _global_logger.handlers.clear()
    _global_logger.addHandler(handler)
    _global_logger.addHandler(stream_handler)

    return _global_logger


# Set up logging
script_name = os.path.splitext(os.path.basename(__file__))[0]
logger = init_logger(script_name)


def save_or_update(domain: str, rr: str, value: str):
    r = get_txt_record(domain, rr)

    if r:
        logger.debug(f"Updating value of txt record: rr={rr}, value={value}")
        update_txt_record(r, value)
    else:
        logger.debug(f"Adding txt record as it is not found: rr={rr}, value={value}")
        add_txt_record(domain, rr, value)


def get_txt_record(domain: str, rr: str) -> models.DescribeDomainRecordsResponseBodyDomainRecordsRecord | None:
    client = Client(config)

    request = models.DescribeDomainRecordsRequest(domain_name=domain, type='TXT')

    response = client.describe_domain_records(request)
    for it in response.body.domain_records.record:
        if it.rr == rr:
            return it

    return None


def add_txt_record(domain: str, rr: str, value: str):
    request = models.AddDomainRecordRequest(domain_name=domain, rr=rr, type='TXT', value=value)
    Client(config).add_domain_record(request)


def update_txt_record(r: models.DescribeDomainRecordsResponseBodyDomainRecordsRecord, value: str):
    request = models.UpdateDomainRecordRequest(record_id=r.record_id, rr=r.rr, type=r.type, value=value)
    Client(config).update_domain_record(request)

# ################################################ #
# ##### certbot environment variables sample ##### #
# ################################################ #

# 2025-08-21 14:58:58,046 - main.py - 55 - DEBUG - CERTBOT_REMAINING_CHALLENGES=0
# 2025-08-21 14:58:58,047 - main.py - 55 - DEBUG - CERTBOT_DOMAIN=xyz.example.com
# 2025-08-21 14:58:58,048 - main.py - 55 - DEBUG - CERTBOT_VALIDATION=244Ir_qoKxy8i93CGGDcL4XW-dRGmRJNg2tw_Uyzf80
# 2025-08-21 14:58:58,049 - main.py - 55 - DEBUG - CERTBOT_ALL_DOMAINS=xyz.example.com

if __name__ == '__main__':
    for (k, v) in os.environ.items():
        logger.debug(f'{k}={v}')

    certbot_domain = os.environ['CERTBOT_DOMAIN']
    certbot_validation = os.environ['CERTBOT_VALIDATION']

    domain = '.'.join(certbot_domain.split('.')[-2:])
    subdomain = ''.join(certbot_domain.split('.')[:-2])
    logger.debug(f'domain={domain}, subdomain={subdomain}')

    rr = '_acme-challenge'
    if subdomain:
        rr += f'.{subdomain}'

    save_or_update(domain, rr, certbot_validation)
