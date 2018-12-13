# crypto-news-analyzer

## Dependencies

The project has a lot of common dependencies. We manage them with pipenv. Make sure you have the latest version with:

```
$ pip install --user --upgrade pipenv
```

Install dependencies with:

```
pipenv install
```

## Running scripts

You can run any python script within the pipenv environment by using:

```
pipenv run --three /path/to/script.py
```

Alternativly, you can start a shell with the environment with:

```
pipenv shell
```

Scripts can be run by utilization of make:

```
  $ make <procedure>
```

please see makefile for available commands.
