from setuptools import setup

setup(
    name='jay',
    version='0.1',
    py_modules=['jay'],
    install_requires=[
        'Click',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        jay=jay:cli
    ''',
)
