# Contributing

## Code of Conduct

Before contributing, please take time to review our code of conduct [here](CODE_OF_CONDUCT.md).

## Developer Cookbook

### Cloning the Git Repository

    $ git clone https://github.com/ebenh/django-flex-user/ django-flex-user

### Setting Up the Django Project

Refer to the
docs [here](https://django-flex-user.readthedocs.io/en/latest/reference_project.html#running-the-reference-project-locally)
to learn how to set up the Django project.

### Publishing to PyPI

1. Update `MANIFEST.in` to include any new, non-source files you may have added.

2. Build the Python package.

        $ python setup.py sdist

3. Install and/or upgrade `twine`.

        $ python3 -m pip install --upgrade twine

4. Upload the package to the PyPI test repository.

        $ python3 -m twine upload --repository testpypi dist/*

   > Note: Username is `__token__` and password is your token for the test repository (make sure to include the `pypi-`
   > prefix).

5. Test the package you just uploaded to the PyPI test repository. The value of `${VERSION}` should be the package's
   current semantic version (e.g. `1.0.0`).

        $ python3 -m pip install --user django-flex-user/dist/django-flex-user-${VERSION}.tar.gz

6. If the above command completes without errors, bump the version number, tag the release and commit.

        $ bumpversion <major|minor|patch> && git push --tags

8. Build the Python package again in order to capture the updated version number.

        $ python setup.py sdist

8. If the above commands execute without any errors, you're ready to upload the library to PyPI. The value
   of `${VERSION}` should be the package's latest semantic version (e.g. `2.0.0`).

        $ python3 -m twine upload dist/django-flex-user-${VERSION}.tar.gz

   > Note:  Username is `__token__` and password is your PyPI token (make sure to include the `pypi-` prefix).

9. Optionally, clean your working tree.

        $ git clean -idx
