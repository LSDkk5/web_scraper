# SCRAPER SERVICE

### Install dependents

```sh
$ pip install -r src/REQUIREMENTS.txt
```

### Configure daemon
```sh
sudo vim /lib/systemd/system/web-scrap.service
```
```sh
[Unit]
Description=Dummy Service
After=multi-user.target
Conflicts=getty@tty1.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 /usr/bin/web-scrap.py
StandardInput=tty-force

[Install]
WantedBy=multi-user.target
```

### Reload systemctl daemon
```sh
sudo systemctl daemon-reload
```

```sh
sudo systemctl enable web-scrap.service #enable serivce
sudo systemctl start web-scrap.service #start service
sudo systemctl start web-scrap.service #start service
```