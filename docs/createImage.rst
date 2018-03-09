Creating an Image
=================

This instructions will create an image for a Raspberry Pi that can be downloaded to help get folks started quickly with Brewery Pi.

Download the Latest Raspbian *Lite* Image
-----------------------------------------

.. _latest Raspbian Lite image here: https://www.raspberrypi.org/downloads/raspbian/

You can find the `latest Raspbian Lite image here`_.

Once downloaded, extract the image to somewhere on a computers' (not yourRaspberry Pi) hard drive.

Write the Raspbian *Lite* Image to your Memory Card
---------------------------------------------------

.. _installing operating system images here: https://www.raspberrypi.org/documentation/installation/installing-images/README.md

I'm doing this on Windows 10 and use Win32 Disk Imager. You can find more details on the Raspberry Pi website regarding `installing operating system images
here`_. Once the image is written to the memory card, place an empty file named "ssh" in the root of memory card. This will allow us to install and configure
the Raspberry Pi without having to hookup a keyboard, mouse or monitor (headless configuration). Once this is done, "eject" the memory card so you can safely
remove it. You can now install the memory card into your Raspberry Pi.

Connect to the Raspberry Pi using SSH
-------------------------------------

.. _finding your IP address here: https://www.raspberrypi.org/documentation/remote-access/ip-address.md

With the power to your Raspberry Pi off, plug it into your network (or laptop ethernet port) using the ethernet port. Next connect the power supply to the
Raspberry Pi and plug it in.

Now you need to find the IP address that is assigned to your Raspberry Pi. This is dependent on your network. You can find more details on the Raspberry Pi
website regarding `finding your IP address here`_.

Once you know the IP address of your Raspberry Pi, connect to it using your SSH client. The default login is "pi" and password is "raspberry".

Configure and Update the Raspberry Pi
-------------------------------------

Once logged in change the password of pi user to "brewery"::

    $ sudo passwd pi

Change the hostname of the Raspberry Pi from "raspberrypi" to "brewerypi" in /etc/hostname, save and exit.::

    $ sudo nano /etc/hostname

Next update the software on your Raspberry Pi::

    $ sudo apt-get update
    $ sudo apt-get -y upgrade

Install MySQL (MariaDB)
-----------------------
::

    $ sudo apt-get -y install mysql-server

Configure MySQL (MariaDB)
-------------------------
::

    $ sudo mysql
    > CREATE DATABASE BreweryPi;
    > CREATE USER 'pi'@'%' IDENTIFIED BY 'brewery';
    > GRANT ALL ON BreweryPi.* TO 'pi'@'%';
    > CREATE USER 'grafanaReader'@'%' IDENTIFIED BY 'brewery';
    > GRANT SELECT ON BreweryPi.* TO 'grafanaReader';
    > GRANT EXECUTE ON BreweryPi.* TO 'grafanaReader';
    > quit
    $ sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf

Comment out, with the '#' character, "bind-address = 127.0.0.1. Save and exit.::

    $ sudo service mysql restart

Install Brewery Pi
------------------
::

    $ nano ~/.profile`

Add the following to the end of the file, save and exit::

    export FLASK_APP=breweryPi.py

Logout and then log back in.
::

    $ sudo apt-get -y install git
    $ git clone https://github.com/DeschutesBrewery/brewerypi
    $ cd brewerypi
    $ git checkout vX.Y.Z
    $ sudo apt-get -y install python3-venv
    $ python3 -m venv venv
    $ source venv/bin/activate
    (venv) $ pip install -r requirements.txt
    (venv) $ flask db upgrade
    (venv) $ sudo mysql BreweryPi < db/storedProcedures/spElementSummary.sql
    (venv) $ flask run --host 0.0.0.0

Point a web browser at http\://<Your Raspberry Pi IP Address>:5000 and verify that you can access the app.

CTRL+C to quit

Test gunicorn::

    (venv) $ gunicorn -b 0.0.0.0:5000 -w 2 breweryPi:app

Point a web browser at http\://<Your Raspberry Pi IP Address>:5000 and verify that you can access the app.

CTRL+C to quit

Deployment with Supervisor
--------------------------
::

    $ sudo apt-get -y install supervisor
    $ sudo nano /etc/supervisor/conf.d/brewerypi.conf

Add the following to the file and save::

    [program:breweryPi]
    command=/home/pi/brewerypi/venv/bin/gunicorn -b 0.0.0.0:5000 -w 2 breweryPi:app
    directory=/home/pi/brewerypi
    user=pi
    autostart=true
    autorestart=true
    stopasgroup=true
    killasgroup=true

Reload Supervisor with the following command::

    $ sudo supervisorctl reload

Grafana
-------
::

    $ sudo apt-get -y install adduser libfontconfig
    $ curl -L https://github.com/fg2it/grafana-on-raspberry/releases/download/vX.Y.Z/grafana_4.6.3_armhf.deb -o /tmp/grafana_4.6.3_armhf.deb
    $ sudo dpkg -i /tmp/grafana_X.Y.Z_armhf.deb
    $ rm /tmp/grafana_X.Y.Z_armhf.deb

Run the following commands to start Grafana at boot::

    $ sudo /bin/systemctl daemon-reload
    $ sudo /bin/systemctl enable grafana-server

Reboot and point a web browser at http\://<Your Raspberry Pi IP Address>:3000

Login with "admin" for both the user and password.

Click on "Add data source" and set the following properties:

+----------+---------------+
| Property | Value         |
+==========+===============+
| Name     | BreweryPi     |
+----------+---------------+
| Type     | MySQL         |
+----------+---------------+
| Database | BreweryPi     |
+----------+---------------+
| User     | grafanaReader |
+----------+---------------+
| Password | brewery       |
+----------+---------------+

Download the Brewery Pi release source files from GitHub and import the Grafana dashboards.

Create a Compressed Image
-------------------------

.. _Shrinking Raspberry Pi SD Card Images: http://www.aoakley.com/articles/2015-10-09-resizing-sd-images.php
.. _How to BackUp and Shrink Your Raspberry Pi Image: http://www.instructables.com/id/How-to-BackUp-and-Shrink-Your-Raspberry-Pi-Image/

I referenced both of these articles for this process:

`Shrinking Raspberry Pi SD Card Images`_

`How to BackUp and Shrink Your Raspberry Pi Image`_

You need a Linux distribution for this task and an external disk drive. I'm using VMware Workstation Player and Debian 64-bit distribution.
Shutdown the Raspberry Pi and eject the disk. Using Win32 Disk Imager, read the Raspberry Pi data from the SD card to an image file on the external drive named
brewerypi-vX.Y.Z.img (substitute "X", "Y" and "Z" for the release version). Install the following tools on the VMWare Workstation Player::

    $ su
    $ apt-get update
    $ apt-get -y install dcfldd
    $ apt-get -y install gparted
    $ apt-get -y install zip

Connect the external drive to the VMWare Workstation Player.
Execute the following command and take note of the "Start" sector of the second partition which will be referenced as "START" below.
::

    $ sudo fdisk -l brewerypi-vX.Y.Z.img

Execute the following, remembering to replace "START" with the value of the start sector you noted above.
::

    $ losetup /dev/loop0 brewerypi-vX.Y.Z.img -o $((START*512))
    $ gparted /dev/loop0

Right click on the /dev/loop0 partition and choose "Resize/Move". Finding the minimum size is a bit of trial and error.
Start by using 700 MB above the listed minimum size. Select "Apply All Operations".
If the resize fails, increase the size by another 50 MB and try again until successful.
Once the partition is successfully resized, expand the "shrink file system" under "Details" and note the value listed with "resize2fs -p /dev/loop0" which
will be referenced as "RESIZE" below. Now execute the following::

    $ losetup -d /dev/loop0
    $ losetup /dev/loop0 brewerypi-vX.Y.Z.img
    $ fdisk /dev/loop0

Within fdisk, execute the following sequence::

    d <Enter>
    2 <Enter>
    n <Enter>
    p <Enter>
    2 <Enter>
    START <Enter>
    +RESIZEK <Enter> (don't forget the 'K' or 'M' after RESIZE)
    w <Enter>
    N <Enter> (for remove signature)

Once fdisk exits, execute the following commands::

    $ fdisk -l /dev/loop0
    $ losetup -d /dev/loop0

Record the "End" sector of the second partition which will be referenced as "END" below.
::

    $ truncate -s $(((END+1)*512)) brewerypi-vX.Y.Z.img
    $ losetup /dev/loop0 brewerypi-vX.Y.Z.img -o $((START*512))
    $ mkdir -p /mnt/imageroot
    $ mount /dev/loop0 /mnt/imageroot
    $ dcfldd if=/dev/zero of=/mnt/imageroot/zero.txt
    $ rm /mnt/imageroot/zero.txt
    $ umount /mnt/imageroot
    $ rmdir /mnt/imageroot
    $ losetup -d /dev/loop0
    $ zip brewerypi-vX.Y.Z.zip brewerypi-vX.Y.Z.img

brewerypi-vX.Y.Z.zip will contain a compressed image to install on a Raspberry Pi.
