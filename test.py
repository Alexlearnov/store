from sqlalchemy import select

from app.models.categories import Category

# Составление запроса
stmt = select(Category).where(Category.is_active == True).order_by(Category.name)

print(stmt)
