# dizqueTV-python
[![PyPi](https://img.shields.io/pypi/dm/dizquetv?color=green&label=PyPi%20downloads&logo=Pypi&logoColor=orange&style=flat-square)](https://pypi.org/project/dizqueTV/)
[![Python support](https://img.shields.io/pypi/pyversions/dizquetv?color=purple&label=Python%20support&logo=python&logoColor=yellow&style=flat-square)]()
[![License](https://img.shields.io/pypi/l/dizquetv?color=orange&style=flat-square)](https://github.com/nwithan8/dizqueTV-python/blob/master/LICENSE)

[![Open Issues](https://img.shields.io/github/issues-raw/nwithan8/dizqueTV-python?color=gold&style=flat-square)](https://github.com/nwithan8/dizqueTV-python/issues?q=is%3Aopen+is%3Aissue)
[![Closed Issues](https://img.shields.io/github/issues-closed-raw/nwithan8/dizqueTV-python?color=black&style=flat-square)](https://github.com/nwithan8/dizqueTV-python/issues?q=is%3Aissue+is%3Aclosed)
[![Activity](https://img.shields.io/github/commit-activity/m/nwithan8/dizqueTV-python?color=red&style=flat-square)]()

[![Latest Release](https://img.shields.io/github/v/release/nwithan8/dizqueTV-python?color=red&label=latest%20release&logo=github&style=flat-square)](https://github.com/nwithan8/dizqueTV-python/releases)
[![Docs](https://img.shields.io/readthedocs/dizquetv?style=flat-square)](http://dizquetv.readthedocs.io/)

[![Discord](https://img.shields.io/discord/472537215457689601?color=blue&logo=discord&style=flat-square)](https://discord.gg/7jGbCJQ)
[![Twitter](https://img.shields.io/twitter/follow/nwithan8?label=%40nwithan8&logo=twitter&style=flat-square)](https://twitter.com/nwithan8)

A Python library to interact with a [dizqueTV](https://github.com/vexorian/dizquetv) instance

## Installation
#### From GitHub
1. Clone repository with ``git clone https://github.com/nwithan8/dizqueTV-python.git``
2. Enter project folder with ``cd dizqueTV-python``
3. Install requirements with ``pip install -r requirements.txt``

#### From PyPi
Run ``pip install dizqueTV``

## Setup
Import the ``API`` class from the ``dizqueTV`` module

Ex.
```
from dizqueTV import API

dtv = API(url="http://localhost:8000")
```
Enable verbose logging by passing ``verbose=True`` into the ``API`` object declaration
 
 
## Usage

Documentation available on [ReadTheDocs](https://dizquetv.readthedocs.io/en/latest/)

### Exceptions
- ``MissingSettingsError``: The kwargs you have provided to create a new object (ex. ``Channel`` or ``PlexServer``) are incomplete
- ``MissingParametersError``: You did not provide a required parameter in your function call (ex. provide a PlexAPI Server when adding PlexAPI Video to a channel)
- ``NotRemoteObjectError``: The object you are calling this method on is a locally-created object that does not exist on the dizqueTV server
- ``ChannelCreationError``: An error occurred when creating a Channel object

## Contact
Please leave a pull request if you would like to contribute.

Join the dizqueTV Discord server (link on [project page](https://github.com/vexorian/dizquetv)). My Discord username is **nwithan8#8438**

Follow me on Twitter: [@nwithan8](https://twitter.com/nwithan8)

Also feel free to check out my other projects here on [GitHub](https://github.com/nwithan8) or join the #developer channel in my Discord server below.

<div align="center">
	<p>
		<a href="https://discord.gg/ygRDVE9"><img src="https://discordapp.com/api/guilds/472537215457689601/widget.png?style=banner2" alt="" /></a>
	</p>
</div>
