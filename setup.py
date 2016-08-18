
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

long_desc=open('README.rst','r').read()

setup(name="slacker-python",
      version="0.4.1",
      author="Sun Ning",
      author_email="sunng@about.me",
      description="python client of slacker RPC",
      long_description=long_desc,
      url="http://github.com/sunng87/slacker-python",
      license='mit',
      packages=['slacker'],
      package_data={'': ['README.rst']},
      install_requires=['pyclj==0.2.1',
                        'gevent==1.1.0',
                        'kazoo==2.2.1'],
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Topic :: Software Development',
                   "Programming Language :: Python :: 2",
                   'Programming Language :: Python :: 2.7',
                   'Operating System :: OS Independent']
    )
