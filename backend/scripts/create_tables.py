from app.database.db import Base
from app.database.db import engine

from app.models.document import Document

Base.metadata.create_all(bind=engine)

print("Tables created successfully")