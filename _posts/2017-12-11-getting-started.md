---
title:  "Getting Started"
date:   2018-01-01 16:36:06 -0800
---
These instructions will get you a Brewery Pi production environment on a Raspberry Pi.

If you have questions about these instructions, make sure to read the post on "Brewery Pi Hardware" [here](http://brewerypi.com/2017/12/02/brewery-pi-hardware.html).

# 1. Download the Latest Brewery Pi Image

You can find the latest releases and images (starting with release v0.2.1) to download [here](https://github.com/DeschutesBrewery/brewerypi/releases).

Once downloaded, extract the image to somewhere on your computer's hard drive.

# 2. Write the Brewery Pi Image to your Memory Card

I'm doing this on Windows 10 and use Win32DiskImager. You can find more details on the Raspberry Pi website regarding installing operating system images [here](https://www.raspberrypi.org/documentation/installation/installing-images/README.md).

Once this is done, "eject" the memory card so you can safely remove it. You can now install the memory card into your Raspberry Pi.

# 3. Connect to the Rapsberry Pi using SSH

First you'll need a SSH client. I use PuTTY which you can find [here](http://www.putty.org/), but you can use any SSH client you prefer.

With the power to your Raspberry Pi off, plug it into your network (or laptop ethernet port) using the ethernet port. Next connect the power supply to the Raspberry Pi and plug it in.

Now you need to find the IP address that is assigned to your Raspberry Pi. This is dependent on your network and beyond the scope of this post.

Once you know the IP address of your Raspberry Pi, connect to it using your SSH client. The default login is "pi" and password is "raspberry".

# 4. Configure the Raspberry Pi

```
$ sudo raspi-config
```

Advanced Options->Expand Filesystem

Localisation Options->Change Timezone

Choose "\<Yes>" when promoted "Would you like to reboot now?".

# 4. Access Data Entry Forms and Visualization

Once the Raspberry Pi reboots, verify that you can access the data entry forms and visualizations.

For data entry, point a web browser at:

http://\<Your Raspberry Pi IP Address>:5000

For visualization, point a web browser at:

http://\<Your Raspberry Pi IP Address>:3000

and use "admin" for **both** the "User" and "Password" to log in.
