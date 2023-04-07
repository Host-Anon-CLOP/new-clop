To run:
1) Create `.env` file in likeness to `.env.example`
2) Create `secrets` directory with files in likeness to `secrets-example`
3) Point `SECRETS_DIR` in `.env` to you `secrets` dir. Use absolute full path.
4) Run `docker compose up -d --build` command
5) You may have to restart all containers after first start and soaking for about 3 minutes

To run auto-updater:
1) Run `pip3 install -r requirements.txt`
2) Run `python3 update.py` or set up cron job to run it automatically
