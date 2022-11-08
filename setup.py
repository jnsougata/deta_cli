from setuptools import setup

setup(
    name="deta_cli",
    version="0.0.1",
    description="deta cli wrapper for python",
    url="http://github.com/jnsougata/deta_cli",
    author="jnsougata",
    author_email="jnsougata@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["deta_cli"],
    install_requires=['requests'],
    python_requires=">=3.6",
)