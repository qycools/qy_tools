from setuptools import setup, find_packages

setup(
    name="qy_tools",
    version="0.1.0",
    packages=find_packages(),
    description="A collection of useful Python utilities",
    author="qycools",
    author_email="qiaoyang22@mails.ucas.ac.cn",
    url="https://github.com/qycools/qy_tools",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Add your dependencies here
    ],
)