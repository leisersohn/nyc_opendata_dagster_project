from setuptools import find_packages, setup

setup(
    name="nyc311_dagster_project",
    packages=find_packages(exclude=["nyc311_dagster_project_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
