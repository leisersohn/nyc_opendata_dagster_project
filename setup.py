from setuptools import find_packages, setup

setup(
    name="nyc_opendata_dagster_project",
    packages=find_packages(exclude=["nyc_opendata_dagster_project_tests"]),
    install_requires=[
        "dagster",
        "dagster-webserver",
        "dagster-duckdb",
        "dagster-dbt",
        "dbt-duckdb",
        "pandas",
        "requests"
    ],
    extras_require={"dev": ["dagit", "pytest"]},
)
