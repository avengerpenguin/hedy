import setuptools
from invoke import Collection, task
from . import tasks


__ALL__ = ["app", "setup"]
TASKS = Collection("tasks")


def add_task(t, **project_args):
    @task(
        name=t.name,
        optional=t.optional,
    )
    def wrapped_task(c, **task_args):
        return t(c, **project_args, **task_args)

    wrapped_task.__doc__ = t.__doc__
    TASKS.add_task(wrapped_task, name=t.__name__)


def app(name):
    add_task(tasks.run, name=name)
    add_task(tasks.deb, name=name)
    add_task(tasks.stage)
    return TASKS


def setup(name, github_owner, **kwargs):
    sensible_defaults = dict(
        name=name,
        use_scm_version={
            "local_scheme": "dirty-tag",
            "write_to": f"{name}/_version.py",
            "fallback_version": "0.0.0",
        },
        long_description="# name",
        long_description_content_type="text/markdown",
        url=f"https://github.com/{github_owner}/{name}",
        packages=[name],
        include_package_data=True,
        classifiers=[
            # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Intended Audience :: Developers",
            "Operating System :: Unix",
            "Operating System :: POSIX",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: Implementation :: CPython",
            "Topic :: Internet :: WWW/HTTP",
        ],
        project_urls={
            "Issue Tracker": f"https://github.com/{github_owner}/{name}/issues",
        },
        setup_requires=[
            "pytest-runner",
            "setuptools_scm>=3.3.1",
            "pre-commit",
        ],
    )

    params = {**sensible_defaults, **kwargs}
    setuptools.setup(**params)
