import setuptools
import dizqueTV._info as package_info

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", 'r') as fh:
    requirements = fh.read().splitlines()

with open("dev_requirements.txt", 'r') as fh:
    dev_requirements = fh.read().splitlines()

setuptools.setup(
    name=package_info.__title__,  # How you named your package folder (MyLib)
    packages=setuptools.find_packages(),  # Choose the same as "name"
    version=package_info.__version__,  # Start with a small number and increase it with every change you make
    license=package_info.__license__,
    description=package_info.__description__,  # Give a short description about your library
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=package_info.__author__,  # Type in your name
    author_email=package_info.__author_email__,  # Type in your E-Mail
    url='https://github.com/nwithan8/dizqueTV-python',  # Provide either the link to your github or to your website
    download_url=f'https://github.com/nwithan8/dizqueTV-python/archive/refs/tags/{package_info.__version__}.tar.gz',
    keywords=package_info.__keywords__,  # Keywords that define your package best
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
    },
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 4 - Beta',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',  # Specify which python versions that you want to support
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia',
        'Topic :: Internet :: WWW/HTTP',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.7'
)
