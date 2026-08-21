# Deployment

The repository contains code and migrations, but not the SQLite database. After pulling new code in production, run these commands from the project directory:

```bash
source /home/mattstevensonadmin/.virtualenvs/venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Add the following PythonAnywhere scheduled task to run hourly (use the
project's virtualenv Python path):

```bash
/home/mattstevensonadmin/.virtualenvs/venv/bin/python /home/mattstevensonadmin/mattstevensonmusic/manage.py record_visitor_count
```

The command stores a timestamped snapshot of that day's unique visitors in
the `VisitorCountSnapshot` table. Visitor identity is kept in a one-way hash
of a random browser cookie; IP addresses are not stored.

Restart the web application after these commands.

The production web server must serve these directories directly; Gunicorn/Django
should not be responsible for media or static files in production. For Nginx,
the site configuration should include:

```nginx
location /static/ {
	alias /home/mattstevensonadmin/mattstevensonmusic/staticfiles/;
}

location /media/ {
	alias /home/mattstevensonadmin/mattstevensonmusic/media/;
}
```

After changing the Nginx configuration, run `sudo nginx -t` and reload Nginx.
The `media/` directory must contain every file referenced by the production
database. This includes uploaded songs under `media/songs/` and silent movies
under `media/movies/`; back up these directories alongside the database. The
reported `timeWas_cover_SUBVERT.png` file is not in this
repository, so restore it to
`media/posts/top-images/timeWas_cover_SUBVERT.png` or update that post in the
admin to use an existing upload before reloading the site.

The Interactive page accepts browser-supported audio such as MP3, AAC, or OGG
and video such as MP4 with H.264 video. Configure the production web server to
send the correct `Content-Type` headers and support HTTP byte-range requests;
native browser audio and video controls rely on both for reliable seeking and
streaming. Effect settings are stored as JSON on each song and are edited in
the Django admin.

Production environment variables should include:

```dotenv
DJANGO_SECRET_KEY=<long-random-production-secret>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.example,www.your-domain.example
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.example,https://www.your-domain.example
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SECURE_HSTS_SECONDS=31536000
DJANGO_DB_ENGINE=django.db.backends.sqlite3
DJANGO_DB_NAME=/home/mattstevensonadmin/mattstevensonmusic/db.sqlite3
CONTACT_EMAIL=your-inbox@example.com
DJANGO_DEFAULT_FROM_EMAIL=your-pythonanywhere-username@users.pythonanywhere.com
DJANGO_EMAIL_HOST=smtp.pythonanywhere.com
DJANGO_EMAIL_PORT=587
DJANGO_EMAIL_HOST_USER=your-pythonanywhere-username
DJANGO_EMAIL_HOST_PASSWORD=your-pythonanywhere-password
DJANGO_EMAIL_USE_TLS=True
DJANGO_EMAIL_TIMEOUT=10
```

For a PythonAnywhere deployment, use the PythonAnywhere account username and
password for SMTP authentication. The `DJANGO_DEFAULT_FROM_EMAIL` address must
be an address that PythonAnywhere permits for that account; start with the
account's `@users.pythonanywhere.com` address. Set these variables in the web
app environment or in the deployed project's `.env`, then reload the web app.
Do not put the password in git.

Keep the production database and `media/` directory on persistent storage. They are not included in git, so a new or reset server needs migrations and a content restore before serving traffic.
