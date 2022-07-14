# Setup


## Setup Virtual Environment

```bash
python3 venv env
```

```bash
source ./env/bin/activate
```

## Install Requirements

```bash
python3 -m pip install -r requirements.txt
```

## Migrate

```bash
./manage.py makemigrations
```

```bash
./manage.py migrate
```

## Seed Group

```bash
./manage.py shell
```

```python3
from api.seeders import generate_groups
generate_groups()
```

## Run Server

```bash
./manage.py runserver
```