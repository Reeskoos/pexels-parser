import os

from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get('API_KEY')
PROXY_LOGIN = os.environ.get('PROXY_LOGIN')
PROXY_PASS = os.environ.get('PROXY_PASS')
PROXY_IP = os.environ.get('PROXY_IP')
