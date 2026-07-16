from setuptools import setup

setup(
    name='mdconvert',
    version='0.1.0',
    py_modules=['mdconvert'],
    install_requires=[
        'click>=8.1.0',
        'pyperclip>=1.8.0',
    ],
    entry_points={
        'console_scripts': [
            'mdconvert=mdconvert:cli',
        ],
    },
    author='Your Name',
    description='Smart Markdown converter for Claude token optimization',
    python_requires='>=3.9',
)