from setuptools import setup, find_packages

version = '0.1.0'

setup(name="helga-jeopardy",
      version=version,
      description=('HALP'),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='irc bot jeopardy',
      author='Justin Caratzas',
      author_email='bigjust@lambdaphil.es',
      license='LICENSE',
      packages=find_packages(),
      install_requires = (
          'requests>=2.0.0',
      ),
      include_package_data=True,
      py_modules=['helga_jeopardy'],
      zip_safe=True,
      entry_points = dict(
          helga_plugins = [
              'jeopardy = helga_jeopardy:jeopardy',
          ],
      ),
)
