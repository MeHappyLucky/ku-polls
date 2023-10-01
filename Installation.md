## How to Install the app
Open the Terminal and follow these steps

1. Clone or download the code from Github

```
git clone https://github.com/MeHappyLucky/ku-polls.git
cd ku-polls
```

2. Create a virtual environment and install dependencies

```
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
```

3. How to set values for externalized variables

```
copy sample.env .env
```

4. Edit the `.env` file

```
SECRET_KEY=(anything you like)
DEBUG=True
```

4. Run migrations

```
python manage.py migrate
```

5. Run tests

```
python manage.py test
```

6. Install data from the data fixtures

```
python manage.py loaddata data/users.json
python manage.py loaddata data/polls-v2.json
```
