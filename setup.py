from setuptools import setup, find_packages

setup(
    name="post",
    version="0.0.1.b",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    py_modules=["main"],
    entry_points={
        "console_scripts": [
            "post = post.main:main",
        ],
    },
    install_requires=["paramiko", "types-paramiko", "typing_extensions", "pyqt6", "pyqtdarktheme", "pyyaml", "flask", "flasgger"],
)
