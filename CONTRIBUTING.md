# Contributing

Thank you for your interest in contributing to the `iso639` codebase!

If you would like to add or update a feature in `iso639`,
it is recommended that you first file a GitHub issue to discuss your proposed changes
and check their compatibility with the rest of the package before making a pull request.

## Setting up a Development Environment

To contribute changes to `iso639`,
you'll need to
[create a fork of this repo at your GitHub account](https://github.com/jacksonllee/iso639/fork).
After that, you'll download the source code from your fork,
and install the package in the "editable" mode for development work: 

```bash
git clone https://github.com/<your-github-username>/iso639.git
cd iso639
pip install -r dev-requirements.txt
pip install -e .
```

## Working on a Feature or Bug Fix

The development steps below assume that your local Git repo has a remote
`upstream` link to `jacksonllee/iso639`:

```bash
git remote add upstream https://github.com/jacksonllee/iso639.git
```

After this step (which you only have to do once),
running `git remote -v` should show your local Git repo
has links to both "origin" (pointing to your fork `<your-github-username>/iso639`)
and "upstream" (pointing to `jacksonllee/iso639`).

To work on a feature or bug fix:

1. Before doing any work, check out the `main` branch and
   make sure that your local `main` branch is up-to-date with upstream main:

   ```bash
   git checkout main
   git pull upstream main
   ``` 

2. Create a new branch. This branch is where you will make commits of your work.
   (As a best practice, never make commits while on a `main` branch.
   Running `git branch` tells you which branch you are on.)
   
   ```bash
   git checkout -b new-branch-name
   ```
   
3. Make as many commits as needed for your work.

4. When you feel your work is ready for a pull request,
   push your branch to your fork.

   ```bash
   git push origin new-branch-name
   ```
   
5. Go to your fork `https://github.com/<your-github-username>/iso639` and
   create a pull request off of your branch against the `jacksonllee/iso639` repo.

## Running Tests and Code Style Checks

The `iso639` repo has continuous integration (CI) turned on,
with autobuilds running pytest
(for the test suite in [`tests/`](tests))
as well as `black` and `flake8` for consistent code styling.
If an autobuild at an open pull request fails,
then the errors must be fixed by further commits pushed to the branch
by the author before merging is possible.

Work in progress is more than welcome!
If you aren't sure how to, say, add tests to go with your proposed changes,
please still feel free to create a pull request.
We will guide you to polish up your pull request.

If you would like to help avoid wasting free Internet resources
(every push of new commits to an open pull request triggers new CI builds),
you can run pytest/flake8/black checks locally before pushing commits:

```bash
flake8 src tests scripts
black --check src tests scripts
pytest
```
