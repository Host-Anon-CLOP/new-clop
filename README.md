To run:
1) Create `.env` file in likeness to `.env.example`
2) Create `secrets` directory with files in likeness to `secrets-example`
3) Point `SECRETS_DIR` in `.env` to you `secrets` dir. Use absolute full path.
4) Run `docker compose up -d --build` command
5) You may have to restart all containers after first start and soaking for about 3 minutes
6) Alternatively you can run `docker-compose exec web python manage.py collectstatic --noinput` to collect static files for frontend after first start

To run auto-updater:
1) Run `pip3 install -r requirements.txt`
2) Run `python3 update.py` or set up cron job to run it automatically
3) You can use `--no-pull` flag to skip pulling from git (useful for testing)
4) You can use `--environment` (or `-e`) flag to specify environment; Default is `development`; Options are `development`, `test`.
5) You can also run `python3 update.py --help` to see all available options


To create superuser (admin) of the site:
1) Run `docker-compose exec web python manage.py createsuperuser`
2) Follow the instructions
3) You can now log in to the admin panel at `/admin/`
