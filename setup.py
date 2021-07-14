from setuptools import setup

setup(
    name='micropython-urouter',
    version='0.1',
    packages=['urouter'],
    requirements=['micropython-ulogger'],
    #package_dir = {'djangoforandroid': 'djangoforandroid'},

    author='M-Jay',
    author_email='m-jay-1376@qq.com',
    maintainer='M-Jay',
    maintainer_email='m-jay-1376@qq.com',

    #url = 'http://www.pinguino.cc/',
    url='http://urouter.m-jay.cn/',
    download_url='https://github.com/Li-Lian1069/micropython-urouter/releases',

    install_requires=[],

    license='GNU LGPL v3',
    description="A lightweight web server",
    #    long_description = README,
    keywords="micropython",

    classifiers=[
        'Environment :: Web Environment',
        # 'Framework :: Django',
        'Development Status :: 3 - Alpha'
    ],

)