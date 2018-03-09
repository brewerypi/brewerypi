Getting Started
===============

Connect to the Raspberry Pi using SSH
-------------------------------------

.. _finding your IP address here: https://www.raspberrypi.org/documentation/remote-access/ip-address.md
.. _Setting Wi-Fi up via the Command Line here: https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md

I'll be honest, this is going to be the most challenging part of getting your Brewery Pi up and running.

First you'll need a SSH client. I use `PuTTY which you can find here <https://www.putty.org/>`_, but you can use any SSH client you prefer. With the power to
your Raspberry Pi off, plug it into your network (or laptop ethernet port) using the ethernet port. Next connect the power supply to the Raspberry Pi and plug
it in.

Now you need to find the IP address that is assigned to your Raspberry Pi. This is dependent on your network. You can find more details on the Raspberry Pi
website regarding `finding your IP address here`_. If you don't have an IT person for your brewery, this is a good opportunity to find a computer nerd that is
willing to trade their services to get your Brewery Pi up and running on your network in exchange for some beer. You'll want to make sure that your Brewery Pi
has a static IP address so you can bookmark it in your web browser and always find it.

It is preferred to use a wired Ethernet connection to your network vs. Wi-Fi as it is usually faster. However, Wi-Fi is very convenient, so make the decision on
what works best for your brewery. You can find more details on the Raspberry Pi website regarding `Setting Wi-Fi up via the Command Line here`_.

Once you know the IP address of your Raspberry Pi, connect to it using your SSH client. The default login is "pi" and password is "raspberry".
