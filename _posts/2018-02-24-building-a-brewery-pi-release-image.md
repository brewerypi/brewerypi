---
title:  "Building a Brewery Pi Release Image"
date:   2018-02-24 21:19:04 -0800
---
These instructions will get you a Brewery Pi image for a Raspberry Pi.

# 1. Download the Latest Raspbian Lite Image

You can find the latest images to download from [here](https://www.raspberrypi.org/downloads/raspbian/).

Once downloaded, extract the image to somewhere on your computer's hard drive.

# 2. Write the Raspbian Lite Image to your Memory Card

I'm doing this on Windows 10 and use Win32DiskImager. You can find more details on the Raspberry Pi website regarding installing operating system images [here](https://www.raspberrypi.org/documentation/installation/installing-images/README.md).

Once the image is written the memory, place an empty file named "ssh" in the root of memory card. This will allow us to install and configure the Raspberry Pi without having to hookup a keyboard, mouse or monitor.

Once this is done, "eject" the memory card so you can safely remove it. You can now install the memory card into your Raspberry Pi.

# 3. Connect to the Rapsberry Pi using SSH

First you'll need a SSH client. I use PuTTY which you can find [here](http://www.putty.org/), but you can use any SSH client you prefer.

With the power to your Raspberry Pi off, plug it into your network (or laptop ethernet port) using the ethernet port. Next connect the power supply to the Raspberry Pi and plug it in.

Now you need to find the IP address that is assigned to your Raspberry Pi. This is dependent on your network and beyond the scope of this post.

Once you know the IP address of your Raspberry Pi, connect to it using your SSH client. The default login is "pi" and password is "raspberry".

# 4. Update the Rapsberry Pi

Once logged in, update the software on your Raspberry Pi by entering the following commands: 

```
$ sudo apt-get update
$ sudo apt-get -y upgrade
```

# 5. Install MySQL (MariaDB)

```
$ sudo apt-get -y install mysql-server
```

# 6. Configure MySQL (MariaDB)

```
$ sudo mysql
> CREATE DATABASE BreweryPi;
> CREATE USER 'pi'@'%' IDENTIFIED BY 'brewery';
> GRANT ALL ON BreweryPi.* TO 'pi'@'%';
> CREATE USER 'grafanaReader'@'%' IDENTIFIED BY 'brewery';
> GRANT SELECT ON BreweryPi.* TO 'grafanaReader';
> quit
$ sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
```

Comment out, with is '#' character, "bind-address = 127.0.0.1. Save and exit.

```
$ sudo service mysql restart
```

# 7 Install Brewery Pi

```
$ nano ~/.profile`
```

Add the following to the end of the file, save and exit:

```
export FLASK_APP=breweryPi.py
```

Logout and then login.

```
$ sudo apt-get -y install git
$ git clone https://github.com/DeschutesBrewery/brewerypi
$ cd brewerypi
$ git checkout vX.Y.Z
$ sudo apt-get -y install python3-venv
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
(venv) $ python3 -c "import uuid; print(uuid.uuid4().hex)"
```

Will return something like:

```
33696520c8dd42ef8fc6707c4023ddec
```

Copy the entire string and paste it below in .env after "SECRET_KEY="

```
(venv) $ nano .env
```

Add the following to file:

```
SECRET_KEY=33696520c8dd42ef8fc6707c4023ddec
SQLALCHEMY_DATABASE_URI=mysql://pi:brewery@localhost/BreweryPi
```

Save and exit.

```
(venv) $ flask db upgrade
(venv) $ flask run --host 0.0.0.0
```

Point a web browser at http://\<Your Raspberry Pi IP Address>:5000

CTRL+C to quit

Test gunicorn:

```
(venv) $ gunicorn -b 0.0.0.0:5000 -w 2 breweryPi:app
```

Point a web browser at http://\<Your Raspberry Pi IP Address>:5000

CTRL+C to quit

# 8. Deployment

```
$ sudo apt-get -y install supervisor
$ sudo nano /etc/supervisor/conf.d/brewerypi.conf
```

Add the following to the file and save:

```
[program:breweryPi]
command=/home/pi/brewerypi/venv/bin/gunicorn -b 0.0.0.0:5000 -w 2 breweryPi:app
directory=/home/pi/brewerypi
user=pi
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
```

```
$ sudo supervisorctl reload
```

# 9. Grafana

```
$ sudo apt-get -y install adduser libfontconfig
$ curl -L https://github.com/fg2it/grafana-on-raspberry/releases/download/v4.6.3/grafana_4.6.3_armhf.deb -o /tmp/grafana_4.6.3_armhf.deb
$ sudo dpkg -i /tmp/grafana_4.6.3_armhf.deb
$ rm /tmp/grafana_4.6.3_armhf.deb
```
Run the following command to start Grafana at boot:

```
$ sudo /bin/systemctl daemon-reload
$ sudo /bin/systemctl enable grafana-server
```

Reboot and point a web browser at http://\<Your Raspberry Pi IP Address>:3000

Login with "admin" for both the user and password.

Click on "Add data source" and set the following properties:

| Property | Value     |
| -------- | --------- |
| Name     | BreweryPi |
| Type     | MySQL     |
| Database | BreweryPi |
| User     | pi        |
| Password | brewery   |
