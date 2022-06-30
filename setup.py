from setuptools import setup

setup(
	name='zuul-alarm',
	version='0.0.1',
    entry_points={
        'console_scripts': [
            'zuul-alarm=zuul_alarm.run:run'
        ]
    },
)
