---
title:  "Getting Started with Development on Windows"
date:   2017-11-20 15:23:25 -0800
---

These instructions will get you a Brewery Pi development environment on a computer running Windows 10 64-bit.

The following table has the application versions that were successfully used. You can try to use more recent versions at your own risk.

Application | Version
--- | :---:
Git | 2.15.0
Python | 3.6.3
MySQL Server | 5.7.20
MySQL Workbench | 6.3.10

# 1. Install Prerequisite for MySQL

Find the “Visual C++ Redistributable Packages for Visual Studio 2013” from [here](https://www.microsoft.com/en-us/download/details.aspx?id=40784). Click "Download", choose “vcredist_x86.exe” and “vcredist_x64.exe”, hit “Next” then complete the prompts to install.

# 2. Install MySQL Server & MySQL Workbench

Download and run the MySQL installer from [here](https://dev.mysql.com/downloads/windows/installer/5.7.html).

Check "I accept the license terms" at "License Agreement" and click "Next >".

![MySQL - License Agreement]({{ "/assets/2017-11-20-getting-started-with-development-on-windows/mysql-license-agreement.jpg" | absolute_url }})

Choose "Custom" at "Choosing a Setup Type" and click "Next >".

![MySQL - Choosing a Setup Type]({{ "/assets/2017-11-20-getting-started-with-development-on-windows/mysql-choosing-a-setup-type.jpg" | absolute_url }})

Add "MySQL Server 5.7.20 - X64" and "MySQL Workbench 6.3.10 - X64" from "Available Products" to "Products/Features To Be Installed:" and click "Next >".

![MySQL - Select Products and Features]({{ "/assets/2017-11-20-getting-started-with-development-on-windows/mysql-select-products-and-features.jpg" | absolute_url }})

Then click "Execute".

![MySQL - Installation]({{ "/assets/2017-11-20-getting-started-with-development-on-windows/mysql-installation-1.jpg" | absolute_url }})

When the installation has completed click "Next >".

![MySQL - Installation]({{ "/assets/2017-11-20-getting-started-with-development-on-windows/mysql-installation-2.jpg" | absolute_url }})

Click "Next >" when presented with "Product Configuration". 

![MySQL - Product Configuration]({{ "/assets/2017-11-20-getting-started-with-development-on-windows/mysql-product-configuration-1.jpg" | absolute_url }})

Leave the default settings for "Type and Networking" and click "Next >".

![MySQL - Type and Networking]({{ "/assets/2017-11-20-getting-started-with-development-on-windows/mysql-type-and-networking.jpg" | absolute_url }})

For "Accounts and Roles" set the root password to "mysql" and add a user account with "Username" of "pi" and "Password" of "brewery" then click "OK" followed by "Next >".

![MySQL - Accounts and Roles]({{ "/assets/2017-11-20-getting-started-with-development-on-windows/mysql-accounts-and-roles.jpg" | absolute_url }})

Leave the default settings for "Windows Service" and click "Next >".

![MySQL - Windows Service]({{ "/assets/2017-11-20-getting-started-with-development-on-windows/mysql-windows-service.jpg" | absolute_url }})

Leave the default settings for "Plugins and Extensions" and click "Next >".

![MySQL - Plugins and Extensions]({{ "/assets/2017-11-20-getting-started-with-development-on-windows/mysql-plugins-and-extensions.jpg" | absolute_url }})

At "Apply Configuration" press "Execute".

![MySQL - Apply Configuration]({{ "/assets/2017-11-20-getting-started-with-development-on-windows/mysql-apply-configuration-1.jpg" | absolute_url }})

When "Apply Configuration" completes, click "Finish".

![MySQL - Apply Configuration]({{ "/assets/2017-11-20-getting-started-with-development-on-windows/mysql-apply-configuration-2.jpg" | absolute_url }})

When "Product Configuration" for MySQL Server completes, click "Next >".

![MySQL - Product Configuration]({{ "/assets/2017-11-20-getting-started-with-development-on-windows/mysql-product-configuration-1.jpg" | absolute_url }})

Uncheck "Start MySQL Workbench after Setup" and click "Finish" at "Installation Complete".

![MySQL - Installation Complete]({{ "/assets/2017-11-20-getting-started-with-development-on-windows/mysql-installation-complete.jpg" | absolute_url }})

# 3. Install Git

Download and install Git from [here](https://github.com/git-for-windows/git/releases/download/v2.15.0.windows.1/Git-2.15.0-64-bit.exe) using the defaults for installation.

# 4. Install Python

Download the installer for Python 3.6.3 for x86-64 [here](https://www.python.org/ftp/python/3.6.3/python-3.6.3-amd64-webinstall.exe).

At the setup screen check "Add Python 3.6 to PATH" and then select "Install Now".

![MySQL - Choosing a Setup Type]({{ "/assets/2017-11-20-getting-started-with-development-on-windows/python-install-python.jpg" | absolute_url }})

## 4.1 Verify Installation

Launch a new "Windows PowerShell" terminal and confirm that you can start Python by typing "python". Type "quit()" to exit Python.

# 5. Install Visual Studio Code

## 5.1 Configure Prerequisite

Open a "Windows PowerShell" using "Run as administrator" and run the following command:

PS C:\WINDOWS\system32>`Set-ExecutionPolicy RemoteSigned`

Enter 'Y' and press return when prompted. This will allow you to run scripts in PowerShell.

## 5.2 Add MySQL bin Directory to User Path Environment Variable

Type "Edit environment variables for your account" in the Windows search bar.

Select "Path" under "User variables for user" and click "Edit..."

Click "Broswe..." and find the bin directory for MySQL which should be located at "C:\Program Files\MySQL\MySQL Server 5.7\bin".

Click "OK" twice.

## 5.3 Install Visual Studio Code

Download and install Visual Studio Code [here](https://code.visualstudio.com/download) using the defaults.

# 6 Install Virtualenv

Open the integrated terminal in Visual Studio Code (View → Integrated Terminal or Ctrl+~)and enter the following commands:

PS C:\Users\username\Documents>`pip install --upgrade pip setuptools`

PS C:\Users\username\Documents>`pip install virtualenv`

# 7. Configure Brewery Pi

## 7.1 Git Brewery Pi

The following commands will place the project in C:\Users\username\Documents\brewerypi:

PS C:\Users\username>`cd Documents`

PS C:\Users\username\Documents>`git clone https://github.com/DeschutesBrewery/brewerypi`

## 7.2 Create Brewery Pi Database

PS C:\Users\username\Documents>`cd brewerypi`

PS C:\Users\username\Documents\brewerypi>`cmd /c "mysql -u root -p < .\db\brewerypi.sql"`

When prompted for a password enter "mysql".

## 7.3 Configure Brewery Pi Database Permissions

Open MySQL Workbench.

Select "Users and Privileges", then "pi" under "User Accounts". Click on the "Schema Privileges" tab and then "Add Entry..." button.

![MySQL - Users and Privileges 1]({{ "/assets/2017-11-20-getting-started-with-development-on-windows/mysql-users-and-privileges-1.jpg" | absolute_url }})

Click on the "Selected schema:" radio button and make sure "brewerypi" is selected and click the "OK" button.

![MySQL - New Schemea Privilege Definition]({{ "/assets/2017-11-20-getting-started-with-development-on-windows/mysql-new-schema-privilege-definition.jpg" | absolute_url }})

Click the '"Select "All"' button and then press the "Apply" button.

![MySQL - Users and Privileges 2]({{ "/assets/2017-11-20-getting-started-with-development-on-windows/mysql-users-and-privileges-2.jpg" | absolute_url }})

## 7.4 Configure Virtualenv

Make sure you're in the brewerypi folder.

PS C:\Users\username\Documents\brewerypi>`virtualenv venv`

PS C:\Users\username\Documents\brewerypi>`venv\Scripts\activate`

PS C:\Users\username\Documents\brewerypi>`pip install -r requirements.txt`

# 8. Start Brewery Pi

PS C:\Users\username>`cd Documents\brewerypi`

PS C:\Users\username\Documents\brewerypi>`python manage.py runserver`

Point a web browser at [http://127.0.0.1:5000](http://127.0.0.1:5000).
