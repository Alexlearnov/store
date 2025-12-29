from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session

from app.database import get_db_session
from app.models.categories import Category as CategoryModel
from app.schemas import Category as CategorySchema
from app.schemas import CategoryCreate

router = APIRouter(
    prefix="/categories",  # Все эндпоинты в этом файле начинаются с /categories.
    tags=[
        "categories"
    ],  # В Swagger UI эти эндпоинты будут сгруппированы под заголовком "category".
)


@router.get("/", response_model=list[CategorySchema], status_code=status.HTTP_200_OK)
async def get_all_categories(db: Session = Depends(get_db_session)):
    """
    Возвращает список всех активных категорий.
    """
    stmt = select(CategoryModel).where(CategoryModel.is_active)
    categories = db.scalars(stmt).all()
    return categories


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate, db_session: Session = Depends(get_db_session)
):
    """
    Создаёт новую категорию.
    """

    if category.parent_id is not None:
        stmt = select(CategoryModel.id).where(CategoryModel.id == category.parent_id)
        if db_session.scalar(stmt) is None:
            raise HTTPException(status_code=404, detail="Parent Category not found.")

    stmt = (
        insert(CategoryModel).values(**category.model_dump()).returning(CategoryModel)
    )
    new_category = db_session.scalar(stmt)
    db_session.commit()
    return new_category


@router.get(
    "/{category_id}", response_model=CategorySchema, status_code=status.HTTP_200_OK
)
async def update_categor_by_id(
    category_id: int, db_session: Session = Depends(get_db_session)
):
    """
    Получить категорию по её ID.
    """

    if category_id is not None:
        model = db_session.scalar(
            select(CategoryModel).where(CategoryModel.id == category_id)
        )
        return model

    return {"message": f"Категория с ID {category_id} обновлена (заглушка)"}


@router.put("/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int, category: CategoryCreate, db: Session = Depends(get_db_session)
):
    """
    Обновляет категорию по её ID.
    """
    # Проверка существования категории
    stmt = select(CategoryModel).where(
        CategoryModel.id == category_id, CategoryModel.is_active
    )
    db_category = db.scalars(stmt).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    # Проверка существования parent_id, если указан
    if category.parent_id is not None:
        parent_stmt = select(CategoryModel).where(
            CategoryModel.id == category.parent_id, CategoryModel.is_active
        )
        parent = db.scalars(parent_stmt).first()
        if parent is None:
            raise HTTPException(status_code=400, detail="Parent category not found")

    # Обновление категории
    db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(**category.model_dump())
    )
    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(category_id: int, db: Session = Depends(get_db_session)):
    """
    Логически удаляет категорию по её ID, устанавливая is_active=False.
    """
    # Проверка существования активной категории
    stmt = select(CategoryModel).where(
        CategoryModel.id == category_id, CategoryModel.is_active
    )
    category = db.scalars(stmt).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    # Логическое удаление категории (установка is_active=False)
    db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id, CategoryModel.is_active)
        .values(is_active=False)
    )
    db.commit()

    return {"status": "success", "message": "Category marked as inactive"}
