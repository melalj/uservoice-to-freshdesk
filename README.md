# Uservoice to Freshdesk

## Create config.py

```py
FD_API_KEY = '***'
FD_SUBDOMAIN = '***'

UV_SUBDOMAIN = '***'
UV_API_KEY = '***'
UV_API_SECRET = '***'
```

## Run

```sh
virtualenv -p python3 env
source env/bin/activate
pip3 install -r requirements.txt
python3 main.py
```
