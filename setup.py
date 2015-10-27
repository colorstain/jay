from setuptools import setup

setup(
    name='jay',
    author='colorstain',
    author_email="colostain+jay@gmail.com",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ],
    license='MIT',
    version='0.2.0',
    description='Command line tool to check and ssh into AWS EC2 instances',
    py_modules=['jay'],
    install_requires=[
        'Click',
        'boto3'
    ],
    url='https://github.com/colorstain/jay',
    entry_points='''
        [console_scripts]
        jay=jay:cli
    ''',
)
