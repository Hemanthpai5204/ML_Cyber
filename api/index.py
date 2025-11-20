from vercel_wsgi import make_app
from app import app

app = make_app(app)
