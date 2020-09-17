import setuptools
import dizqueTV._version

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='dizqueTV',  # How you named your package folder (MyLib)
    packages=['dizqueTV'],  # Chose the same as "name"
    version=dizqueTV._version.__version__,  # Start with a small number and increase it with every change you make
    license='GNU General Public License v3 (GPLv3)',
    description="Interact with a dizqueTV instance's API",  # Give a short description about your library
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=dizqueTV._version.__author__,  # Type in your name
    author_email='n8gr8gbln@gmail.com',  # Type in your E-Mail
    url='https://github.com/nwithan8/dizqueTV-python',  # Provide either the link to your github or to your website
    download_url=f'https://github.com/nwithan8/dizqueTV-python/archive/{dizqueTV._version.__version__}.tar.gz',  # I explain this later on
    keywords=[
        'dizqueTV',
        'Plex',
        'Jellyfin',
        'Emby',
        'media',
        'API',
        'server',
        'interaction',
        'TV',
        'television',
        'streaming'
    ],  # Keywords that define your package best
    install_requires=[
        'requests',
        'm3u8',
        'plexapi'
    ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 4 - Beta',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',  # Specify which python versions that you want to support
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia',
        'Topic :: Internet :: WWW/HTTP',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.6'
)
