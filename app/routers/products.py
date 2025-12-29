from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session

from app.database import get_db_session
from app.models import Product as ProductModel
from app.schemas import Product as ProductSchema
from app.schemas import ProductCreate

router = APIRouter(
    prefix="/products",
    tags=["products"],  # Группирует эндпоинты под тегом "products" в Swagger UI.
)


@router.get("/", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_all_products(session: Session = Depends(get_db_session)):
    """
    Возвращает список всех товаров.
    """

    products = session.scalars(
        select(ProductModel).where(ProductModel.is_active.is_(True))
    ).all()

    return products


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate, session: Session = Depends(get_db_session)
):
    """
    Создаёт новый товар.
    """

    new_product = session.scalar(
        insert(ProductModel).values(**product.model_dump()).returning(ProductModel)
    )
    session.commit()
    return new_product


@router.get(
    "/category/{category_id}",
    response_model=list[ProductSchema],
    status_code=status.HTTP_200_OK,
)
async def get_products_by_category(
    category_id: int, session: Session = Depends(get_db_session)
):
    """
    Возвращает список товаров в указанной категории по её ID.
    """

    products = session.scalars(
        select(ProductModel).where(
            ProductModel.category_id == category_id, ProductModel.is_active.is_(True)
        )
    ).all()

    return products


@router.get(
    "/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK
)
async def get_product(product_id: int, session: Session = Depends(get_db_session)):
    """
    Возвращает детальную информацию о товаре по его ID.
    """

    product = session.scalar(
        select(ProductModel).where(
            ProductModel.id == product_id, ProductModel.is_active.is_(True)
        )
    )

    if not product:
        raise HTTPException(status_code=404, detail="Not Found.")

    return product


@router.put(
    "/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK
)
def update_product(
    product_id: int,
    product: ProductCreate,
    session: Session = Depends(get_db_session),
):
    """
    Обновляет товар по его ID.
    """

    stmt = (
        update(ProductModel)
        .where(ProductModel.id == product_id, ProductModel.is_active.is_(True))
        .values(**product.model_dump())
        .returning(ProductModel)
    )

    updated: ProductModel | None = session.scalar(stmt)
    if updated is None:
        raise HTTPException(status_code=404, detail="Not Found")

    session.commit()
    return updated


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(product_id: int, session: Session = Depends(get_db_session)):
    """
    Логически удаляет категорию по её ID, устанавливая is_active=False.
    """

    stmt = (
        update(ProductModel)
        .where(
            ProductModel.id == product_id,
            ProductModel.is_active.is_(True),  # явно
        )
        .values(is_active=False)
        .returning(ProductModel.id)
    )

    deleted_id: int | None = session.scalar(stmt)
    if deleted_id is None:
        raise HTTPException(status_code=404, detail="Not Found")

    session.commit()
    return {"status": "success", "message": "Product marked as inactive"}
