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

`$ sudo apt-get upgrade`

Type 'y' when prompted "Do you want to continue?".

# 6. Install MySQL

`$ sudo apt-get install mysql-server`

Type 'y' when prompted "Do you want to continue?".

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

`$ sudo apt-get install python3-flask`

Type 'y' when prompted "Do you want to continue?".

`$ sudo apt-get install python3-pip`

Type 'y' when prompted "Do you want to continue?".

`$ sudo apt-get install git`

Type 'y' when prompted "Do you want to continue?".

`$ sudo pip3 install virtualenv`

`$ git clone https://github.com/DeschutesBrewery/brewerypi`

`$ cd brewerypi`

`$ sudo mysql < db/brewerypi.sql`

`$ nano db/brewerypi.sql`

Do a search and replace of all occurrences of "BreweryPi" with "BreweryPiDemo1". Save the file and exit. Run the following command one more time to create the demo database.

`$ nano db/brewerypi.sql`

`$ sudo mysql < db/brewerypi.sql`

`$ source venv/bin/activate`

`(venv) $ pip install -r requirements`

`(venv) $ python manage.py runserver --host 0.0.0.0`

Point a web browser at http://\<Your Raspberry Pi IP Address>:5000

# 9. Install Gunicorn

`$ cd brewery pi`

`$ source venv/bin/activate`

`$ pip install gunicorn`

`$ gunicorn manage:app --bind=0.0.0.0`

# 10. Grafana

`$ sudo nano /etc/apt/sources.list.d/raspi.list`

Add the following line:

`deb https://packagecloud.io/grafana/stable/debian/ jessie main`

Save the file and exit.

`curl https://packagecloud.io/gpg.key | sudo apt-key add -`

`sudo apt-get update`

`sudo apt-get install grafana`

Type 'y' when prompted "Do you want to continue?".
