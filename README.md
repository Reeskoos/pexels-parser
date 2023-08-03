# Pexel-Parser
Python async parser to download stock images from pexels.com.

Works on asyncio/httpx packages.

## To use it you need:

1. Get API key at https://www.pexels.com/api/.

2. Get proxy.
## Installation
1. Clone repository:
```sh
git clone https://github.com/Reeskoos/pexels-parser.git
```
2. Create virtual enviroment in repository directory:
```sh
python -m venv venv
```
3. Activate it:
```sh
./venv/Scripts/activate
```
4. Run:
```sh
pip install -r requirements.txt
```
5. Create .env file with following code in repository directory:
```sh
API_KEY=YourAPIKey
PROXY_LOGIN=YourProxyLogin
PROXY_PASS=YourProxyPassword
PROXY_IP=YourProxyIP
```
## Usage
Run main.py and follow instructions in console.

Use example:
```sh
[INFO] Welcome to PexelsParser!
Do not use special characters ($%#!* etc.) in your input.
Enter your query: people dancing
```


After complition you can find images in repository_dir/query directory.



