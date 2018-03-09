Creating an Image
=================

Download the Latest Raspbian *Lite* Image
-----------------------------------------

You can find the `latest Raspbian Lite image here <https://www.raspberrypi.org/downloads/raspbian/>`_.

Once downloaded, extract the image to somewhere on a computers' (not your Raspberry Pi) hard drive.

Write the Raspbian *Lite* Image to your Memory Card
---------------------------------------------------

I'm doing this on Windows 10 and use Win32 Disk Imager. You can find more details on the Raspberry Pi website regarding `installing operating system images
here <https://www.raspberrypi.org/documentation/installation/installing-images/README.md>`_.
Once the image is written the memory, place an empty file named "ssh" in the root of memory card.
This will allow us to install and configure the Raspberry Pi without having to hookup a keyboard, mouse or monitor.
Once this is done, "eject" the memory card so you can safely remove it. You can now install the memory card into your Raspberry Pi.

Connect to the Raspberry Pi using SSH
-------------------------------------

With the power to your Raspberry Pi off, plug it into your network (or laptop ethernet port) using the ethernet port.
Next connect the power supply to the Raspberry Pi and plug it in.

Now you need to find the IP address that is assigned to your Raspberry Pi. This is dependent on your network.
You can find more information on finding your Raspberry Pi `IP address here <https://www.raspberrypi.org/documentation/remote-access/ip-address.md>`_.

Once you know the IP address of your Raspberry Pi, connect to it using your SSH client. The default login is "pi" and password is "raspberry".

Update the Raspberry Pi
-----------------------

Once logged in, update the software on your Raspberry Pi::

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
+==========+===============+
| Type     | MySQL         |
+==========+===============+
| Database | BreweryPi     |
+==========+===============+
| User     | grafanaReader |
+==========+===============+
| Password | brewery       |
+==========+===============+


Download the release source files from GitHub and import the dashboards.
