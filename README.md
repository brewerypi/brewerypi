# Brewery Pi

The Brewery Pi project is a historian (for now) designed for craft brewers to allow them to quickly collect and visualize their brewing data enabling them to leverage it to help make better beer for all of us. :beers: Craft brewers operate on a tight budget, so Brewery Pi was designed to run on a Raspberry Pi (starting with the Raspberry Pi 3 Model B) allowing a craft brewery to get started with an investment around $60 USD for the necessary hardware.

## Installation

The easiest way to get started is to download a Brewery Pi image from [GitHub](https://github.com/DeschutesBrewery/brewerypi/releases) for your Raspberry Pi. Brewery Pi follows [semantic versioning]( https://semver.org/) (vX.Y.Z) and you should be able to find images for dot zero (.0) minor releases. For example, if the latest release is v1.3.1, you should be able to find an image for release v1.3.0. Once you have the image installed on a SD card, connect your Raspberry Pi to your network. To get the latest version of Brewery Pi, ssh into your Raspberry Pi. The default username and password are “pi” and “brewery”, respectfully. Once logged in execute the following commands:
```shell
$ sudo supervisorctl stop brewerypi
$ cd ~/brewerypi/
$ git pull
$ git checkout vX.Y.Z (replace vX.Y.Z with target release, for example, v1.3.1)
$ sudo supervisorctl start brewerypi
```
If all goes well, you should now be able to point a web browser to the IP address of your Raspberry Pi to log in to Brewery Pi. Again, use the default username and password of “pi” and “brewery”, respectfully.

## Usage

Checkout the [Getting Started Quickly](https://github.com/DeschutesBrewery/brewerypi/wiki/Getting-Started-Quickly) tutorial.

## Credits

### Contributors

This project exists thanks to all the companies and people who contribute:

[Deschutes Brewery](https://www.deschutesbrewery.com/), [GoodLife Brewing](https://www.goodlifebrewing.com/), [Wild Ride Brewing](https://www.wildridebrew.com/) and [Worthy Brewing](https://worthybrewing.com/).

[Brian Faivre](https://github.com/bfaivre), [Curtis Nelson](https://github.com/c49nelson), [Huck Bales](https://github.com/huckpdx), [Jeremiah Beisner](https://github.com/jmbeisner), [Kyle Kotaich](https://github.com/kkotaich), Nancy-Taylor Mitchell, Paul Bergeman, [Shaelyn Maloney](https://github.com/smaloney2) and [Tim Alexander](https://github.com/tralexander).

## License

See the [LICENSE](https://github.com/DeschutesBrewery/brewerypi/blob/master/LICENSE) file.

# Cheers! :beer:
