from setuptools import setup, find_packages
import sys, os

version = '1.0'
shortdesc ="AGX XML Input/Output"
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()

setup(name='node.ext.xml',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Development Status :: 3 - Alpha',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',     
      ],
      keywords='AGX, Code Generator, XML IO',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url=u'https://svn.plone.org/svn/archetypes/AGX',
      license='GNU General Public Licence',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['node', 'node.ext'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'node',
          'lxml',
          # -*- Extra requirements: -*
      ],
      extras_require = dict(
          test=[
            'interlude',
            'zope.configuration',
          ]
      ),
      entry_points="""
      # -*- Entry points: -*-
      """,
      )