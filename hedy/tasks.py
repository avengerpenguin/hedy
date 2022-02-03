import os
import pathlib
from textwrap import dedent

from invoke import task

DOCKERFILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "Dockerfile.debian"
)


DOCKERFILE_STAGE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "Dockerfile.stage"
)


@task
def run(c, name):
    if not os.path.exists("manage.py"):
        print("No manage.py found; creating default...")
        with open("manage.py", "w") as f:
            f.write(
                dedent(
                    """
            #!/usr/bin/env python


            import sys


            if __name__ == '__main__':
                from django.core.management import execute_from_command_line

                execute_from_command_line(sys.argv)
            """
                )
            )

    package_path = pathlib.Path.cwd() / name

    if not package_path.exists():
        package_path.mkdir()

    settings_path = package_path / "settings.py"
    if not settings_path.exists():
        print("No settings.py found; creating default...")
        with open(settings_path, "w") as f:
            f.write(
                dedent(
                    """
            import django12factor
            d12f = django12factor.factorise()

            DEBUG = d12f['DEBUG']
            """
                )
            )

    c.run(
        f"DJANGO_SETTINGS_MODULE={name}.settings DEBUG=true python manage.py runserver"
    )


@task
def deb(c, name):
    c.run(f"docker build -t hedy-debian-fpm -f {DOCKERFILE} .")
    fpm = "docker run -v $PWD:/app -w /app hedy-debian-fpm"
    version = c.run("python setup.py --version").stdout.strip()
    c.run("rm -rf dist")
    c.run("python setup.py sdist")
    c.run(
        f"{fpm} --verbose --input-type virtualenv --output-type deb "
        f"--name virtualenv-{name} --version {version} --architecture all "
        f"--depends python3-distutils --python-bin /usr/bin/python3 "
        f"--prefix /opt/{name} dist/*"
    )
    c.run(
        f"{fpm} --verbose --input-type dir --output-type deb "
        f"--name {name} --version {version} --depends virtualenv-{name} --architecture all "
        f"--depends apache2 --depends libapache2-mod-wsgi-py3 "
        f"--after-install deb/after-install --config-files /etc deb/etc=/"
    )


@task
def stage(c):
    c.run(f"docker build -t hedy-debian-stage -f {DOCKERFILE_STAGE} .")
    c.run("docker run -it -p 80:80 hedy-debian-stage", pty=True)
