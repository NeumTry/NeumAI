# Contributing to Neum AI

Hello and welcome. Thank you for contributing to Neum AI. Below are some general guidelines to ensure contributions are successful and acknowledged.

Within the Neum AI repo there are two packages: `neumai` and `neumai-tools`. You are welcomed to contribute to both.

## Contents

The `neumai` package is the main package that contains:
- All the core connectors and contructs to build and run data pipelines locally.
- Neum Client that interacts with our REST APIS for the managed cloud service.

The `neumai` package is a collection of experimental features that we are currently working on. See the [README](https://github.com/NeumTry/NeumAI/tree/main/neumai-tools) of the package for a list of the latest features.

## Subtmit a change

To contribute to Neum AI, we ask that you create a PR. 

- Before creating a PR, please check that there is not an open issue or pull request for that change. If there isn't please create an issue so that we know you are working on that and don't duplicate work.
- Once the issue is created, fork the NeumAI repo.
- Make your changes in a branch called `feature/{feature-name}`
- Install the package locally using `pip install -e .` and test. Depending on your change, test all connectors affected by running local pipelines. (We will add built-in tests to help automate this process)
- Open a pull requesta against the `main` branch of the repo. (We will likely change this in the future to have a development branch)

## What happens next

We will review your PR as soon as possible. Once we approve, we will merge the changes. We try to generate a package update every couple days and so your changes will be released once we cut the next version.
