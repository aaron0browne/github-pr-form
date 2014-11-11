from setuptools import setup, find_packages
setup(
    name = 'github-pr-form',
    version = '0.1',
    packages = find_packages(),
    install_requires = [
        'github3.py==0.9.3',
        'sh==1.09',
        'click==3.3',
        'markdown2==2.3.0',
        'selenium==2.44.0'
    ],
    entry_points = {
        'console_scripts': [
            'ghform = ghform.cli:cli'
        ]
    }
)
