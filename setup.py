#!/usr/bin/env python
#-*-coding:utf-8-*-

# Copyright (C) - 2011 Marcel Pinheiro Caraciolo  <marcel @orygens.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from setuptools import setup, find_packages
import pyfoursquare

name = 'pyfoursquare'

version = str(pyfoursquare.__version__)


setup(name=name,
      version=version,
      description="Python Wrapper for Foursquare (http://foursquare.com/) API",
      author="Marcel Caraciolo",
      author_email='caraciol@gmail.com',
      long_description="""
      Python Wrapper for Foursquare (http://foursquare.com/) API
      """,
      url="https://github.com/marcelcaraciolo/foursquare",
      download_url='https://github.com/marcelcaraciolo/foursquare/tarball/master',
      license="MIT",
      keywords="foursquare library api",
      classifiers=[
                   "Development Status :: 4 - Beta",
                   "Topic :: Utilities",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 2",
                   "Topic :: Internet",
                   "Topic :: Internet :: WWW/HTTP",
                   ],
      packages=find_packages(),
)
