
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

long_desc=open('README.rst','r').read()

setup(name="slacker-python",
      version="0.1.2",
      author="Sun Ning",
      author_email="sunng@about.me",
      description="python client of slacker RPC",
      long_description=long_desc,
      url="http://github.com/sunng87/slacker-python",
      license='mit',
      packages=['slacker'],
      install_requires=['gevent', 'pyclj'],
      classifiers=['Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Topic :: Software Development',
            'Programming Language :: Python',
            'Operating System :: OS Independent']
    )

