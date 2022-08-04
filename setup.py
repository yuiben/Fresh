from setuptools import setup

setup(
    name="device_management_auth",
    entry_points={
        "console_scripts": [
            "device-management-auth = device_management_auth.__main__:main",
        ],
    },
)
