from setuptools import setup, find_packages

setup(
    name="train-status-scraper",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'selenium==4.16.0',
        'webdriver-manager==4.0.1',
        'beautifulsoup4==4.12.2',
        'requests==2.31.0',
        'python-dotenv==1.0.0',
        'html5lib==1.1',
        'urllib3==2.1.0',
    ],
) 