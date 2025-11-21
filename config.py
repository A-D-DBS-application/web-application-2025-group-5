import os

# Read database URL from environment first; fallback to placeholder
DATABASE_URL = os.environ.get(
	"DATABASE_URL",
	"postgresql://<user>:<password>@<host>:5432/postgres",
)
