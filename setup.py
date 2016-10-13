from setuptools import setup, find_packages

version = '1.0.0'

setup(name="helga-jeopardy",
      version=version,
      description=('HALP'),
      classifiers=['Development Status :: 1 - Beta',
                   'Environment :: IRC',
                   'Intended Audience :: Twisted Developers, IRC Bot Developers',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: IRC Bots'],
      keywords='irc bot jeopardy',
      author='Justin Caratzas',
      author_email='bigjust@lambdaphil.es',
      license='LICENSE',
      packages=find_packages(),
      include_package_data=True,
      py_modules=['helga-jeopardy'],
      zip_safe=True,
      entry_points = dict(
          helga_plugins = [
              'jeopardy= helga_jeopardy:jeopardy',
          ],
      ),
)
