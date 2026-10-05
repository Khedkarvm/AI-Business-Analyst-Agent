
# database.py
## Connect to the database 
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

# print("Database connection created successfully!")


# Create LangChain database object
db = SQLDatabase(engine)

"""# Get usable table names
tables = db.get_usable_table_names()

print("Tables in AI Business Analyst Database:")
for table in tables:
    print("-", table)


# Show table metadata
print("\nTable Metadata:\n")

for table in tables:
    print(f"Table: {table}")
    print(db.get_table_info([table]))
    print("-" * 60)"""