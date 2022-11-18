import setuptools

setuptools.setup(
    name="bkh_ddpm",
    version="0.1",
    author="Bardia Khosravi",
    author_email="bardiakhosravi95@gmail.com",
    description="Personal take on DDPMs",
    url="https://github.com/BardiaKh/DDPM",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "bkh_pytorch_utils>=0.3.8",
        "torchextractor>=3.0.0",
    ],
    python_requires='>=3.8',
)