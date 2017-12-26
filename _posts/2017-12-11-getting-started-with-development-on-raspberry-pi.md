---
title:  "Getting Started with Development on Raspberry Pi"
date:   2017-12-11 04:55:19 -0800
---
These instructions will get you a Brewery Pi development environment on a Raspberry Pi.

If you have questions about these instructions, make sure to read the post on "Brewery Pi Hardware" [here](http://brewerypi.com/2017/12/02/brewery-pi-hardware.html).

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

# 4. Configure the Raspberry Pi

`$ sudo raspi-config`

Advanced Options->Expand Filesystem

Localisation Options->Change Timezone

Choose "<Yes>" when promoted "Would you like to reboot now?". Once the Raspberry Pi reboots, log back in.

# 5. Update the Rapsberry Pi

Once logged in, update the software on your Raspberry Pi by entering the following commands: 

`$ sudo apt-get update`

`$ sudo apt-get -y upgrade`

# 6. Install MySQL

`$ sudo apt-get -y install mysql-server`

# 7. Configure MySQL

`$ sudo mysql`

`> CREATE DATABASE BreweryPi;`

`> CREATE DATABASE BreweryPiDemo1;`

`> CREATE USER 'pi'@'%' IDENTIFIED BY 'brewery';`

`> GRANT ALL ON BreweryPi.* TO 'pi'@'%';`

`> GRANT ALL ON BreweryPiDemo1.* TO 'pi'@'%';`

`> quit`

`$ sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf`

Comment out, with is '#' character, "bind-address = 127.0.0.1. Save and exit.

`$ sudo service mysql restart`

# 8 Install Brewery Pi

`$ nano ~/.profile`

Add the following to the end of the file, save and exit:

```
export FLASK_APP=breweryPi.py
```

Logout and then login.

`$ sudo apt-get -y install git`

`$ git clone https://github.com/DeschutesBrewery/brewerypi`

`$ cd brewerypi`

`$ sudo apt-get -y install python3-venv`

`$ python3 -m venv venv`

`$ source venv/bin/activate`

`(venv) $ pip install -r requirements.txt`

`(venv) $ flask db upgrade`

`(venv) $ sudo mysql BreweryPiDemo1 < db/breweryPiDemo1Data.sql`

`(venv) $ python manage.py runserver --host 0.0.0.0`

Point a web browser at http://\<Your Raspberry Pi IP Address>:5000

# 9. Install Gunicorn

`$ cd brewery pi`

`$ source venv/bin/activate`

`(venv) $ pip install gunicorn`

Test gunicorn:

`(venv) $ gunicorn -b 0.0.0.0:5000 -w 2 manage:app`

# 10. Deployment

`$ echo "export FLASK_APP=manage.py" >> ~/.profile`

`$ sudo apt-get -y install supervisor`

`$ sudo nano /etc/supervisor/conf.d/brewerypi.conf`

Add the following to the file and save:

```
[program:brewerypi]
command=/home/pi/brewerypi/venv/bin/gunicorn -b 0.0.0.0:5000 -w 2 manage:app
directory=/home/pi/brewerypi
user=pi
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
```

`$ sudo supervisorctl reload`

# 11. Grafana

`$ sudo apt-get -y install adduser libfontconfig`

`$ curl -L https://github.com/fg2it/grafana-on-raspberry/releases/download/v4.6.2/grafana_4.6.2_armhf.deb -o /tmp/grafana_4.6.2_armhf.deb`

`$ sudo dpkg -i /tmp/grafana_4.6.2_armhf.deb`

`$ rm /tmp/grafana_4.6.2_armhf.deb`

Run the following command to start Grafana at boot:

`$ sudo systemctl enable grafana-server.service`

Reboot and point a web browser at http://\<Your Raspberry Pi IP Address>:3000
