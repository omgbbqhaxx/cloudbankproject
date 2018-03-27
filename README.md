# Wellcome to CloudBank

It is the most popular and original CloudCoin python script. The code is exceptionally portable and has been used successfully on a very broad range of ubuntu systems and hardware.

## Contact

[![Gitter](https://img.shields.io/gitter/room/nwjs/nw.js.svg)](https://gitter.im/cloudbank-github/)
[![GitHub Issues](https://img.shields.io/badge/open%20issues-0-yellow.svg)](https://github.com/omgbbqhaxx/CloudBank/issues)

- Chat in [cloudbank-github channel on Gitter](https://gitter.im/cloudbank-github).
- Report bugs, issues or feature requests using [GitHub issues](issues/new).



## Getting Started

The CloudBank Documentation site hosts the **[CloudBank homepage](http://cloudbankproject.com/)**, which
has a Quick Start section.

Operating system | Status
---------------- | ----------
Ubuntu and macOS | [![TravisCI](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://travis-ci.org/cloudbank/cloudbank-github)
Windows          | [![AppVeyor](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://ci.appveyor.com/project/cloudbank/cloudbank-github)


```shell
sudo apt-get update -y && sudo apt-get upgrade -y && sudo apt-get install vim -y && sudo apt-get install python-dev -y && sudo apt-get install libevent-dev -y &&  sudo apt-get install python-virtualenv -y && apt-get install git -y
```



## Install python last version..

```shell
sudo apt-get install --reinstall language-pack-en -y
export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8"
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.3
sudo apt-get install python3-pip
apt install python-pip
pip install --upgrade virtualenv
```

## Other configurations..

```shell
virtualenv -p python3 venv
cd venv
. bin/activate
git clone https://github.com/omgbbqhaxx/cloudbankproject.git
mv cloudbankproject cloudbank && cd cloudbank
pip install -r requirements.txt
pipenv install requests
export DJANGO_SETTINGS_MODULE=cloudbank.settings
pip install -U "celery[redis]"
```


## Your need install Redis on your server because celery work with redis server.
**[Step by step installation from here](https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-redis-on-ubuntu-16-04)**

```shell
pip install celery && sudo apt-get update -y && sudo apt-get install build-essential tcl -y && cd /tmp && curl -O http://download.redis.io/redis-stable.tar.gz && tar xzvf redis-stable.tar.gz && cd redis-stable && sudo make install && make && make test
sudo mkdir /etc/redis && cd /etc/redis && wget https://gist.githubusercontent.com/omgbbqhaxx/03b31c2ed319bc987ddb7c8d77c33861/raw/d04c90c96e950c7fb2528774259c3843b20fb7a3/redis.conf
cd /etc/systemd/system/
```



## 4p2p github helper comments.
```shell
git clone https://github.com/omgbbqhaxx/cloudbankproject.git
git pull
git fetch --all
git reset --hard origin/master
```







## Gunicorn configurations
The simplest way to install it is to use pip, a tool for installing and managing Python packages:
```shell
cd /opt/venv/bin
wget https://raw.githubusercontent.com/omgbbqhaxx/cloudbankproject/master/gunicorn_start
chmod u+x gunicorn_start
. gunicorn_start
```

## Circus: A Process & Socket Manager configurations
The simplest way to install it is to use pip, a tool for installing and managing Python packages:
```shell
sudo apt-get install libzmq-dev libevent-dev python-dev python-virtualenv
cd /opt/venv/bin
. activate
git clone https://github.com/omgbbqhaxx/circus-web.git
cd circus-web
python setup.py build
python setup.py install
pip install chaussette
```



example.ini  **[Show docs from here](https://circus.readthedocs.io/en/latest/installation/)**,
```shell
[watcher:startserver]
cmd = /opt/venv/bin/gunicorn_start
numprocesses = 1

[watcher:starttcpconnections]
cmd = python /opt/venv/cloudbank/server.py
numprocesses = 1

[watcher:startcelery]
cmd =/opt/venv/bin/celery --app=cloudbank.mycelery_app:app worker --loglevel=INFO
numprocesses = 1
```



The file is then passed to circusd:
```shell
circusd example.ini
circusd --daemon example.ini
circusctl quit --waiting
```



## Finally we can complate nginx configuration!

NEWER FORGET TO CHANGE SERVER_NAME WITH YOUR IP ADDRESS FROM NGİNXCONF.!
```shell
sudo apt-get install nginx
sudo service nginx start
cd /etc/nginx/sites-available
wget https://raw.githubusercontent.com/omgbbqhaxx/cloudbankproject/master/nginxconf
ln -s /etc/nginx/sites-available/nginxconf /etc/nginx/sites-enabled/nginxconf
cd /opt/venv/
mkdir logs && cd logs
touch nginx-access.log && touch nginx-error.log
```


# REST APIs

## GET Endpoints
 * `http://$yourURL.com/api/v1/createnewwallet/` - allows to create new wallet and private key.

 * `http://$yourURL.com/api/v1/alltransactions/` - allows to get all transactions from database.

 * `http://$yourURL.com/api/v1/gettransaction/$transactionID` - allows to get transaction details.

 * `http://$yourURL.com/api/v1/getwalletfrompkey/$publicKey` - allows to create new wallet and private key.

 * `http://$yourURL.com/api/v1/getpublickeyfromprikey/$privateKEY` - allows to get public key from private key.

 * `http://$yourURL.com/api/v1/getbalance/$wallet` - allows to get last balance from wallet.

 *  `http://$yourURL.com/api/v1/getwalletdetails/$wallet` - allows to get all wallet history.





## POST Endpoints
  * `http://$yourURL.com/api/v1/sendcloudcoin/`
  * `sprikey` sender's private key
  * `receiverwalletallows`  receiver's wallet
  * `amount`  and amount.
  ___


## Donations
  * My ethereum wallet : `0xFBd6f9704478104f0EF3F4f9834c3621210fE598`
  * My Nano wallet : `xrb_1ppmk9ki9kungyer845deysmwokfeughmojxuhorpn7fpiizmka7b3r5jj4z`

## License

[![License](https://img.shields.io/github/license/ethereum/cpp-ethereum.svg)](LICENSE)

All contributions are made under the [GNU General Public License v3](https://www.gnu.org/licenses/gpl-3.0.en.html). See [LICENSE](LICENSE).
