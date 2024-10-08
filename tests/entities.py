from dataclasses import dataclass
from typing import Any, Optional
from datetime import datetime

class BaseData:
    def __getdict__(self) -> dict[str, Any]:
        return {k: v for k, v in vars(self).items()}


@dataclass(slots=True)
class Store(BaseData):
    store_id: str
    slug: str
    is_active: bool
    is_email_verified: bool


class StoreList(BaseData):
    stores: list[Store]

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "StoreList":
        stores_data = data.get("stores", [])
        stores = [
            Store(
                store_id=store.get("id", ""),
                slug=store.get("slug", ""),
                is_active=store.get("is_active", False),
                is_email_verified=store.get("is_email_verified", False),
            )
            for store in stores_data
        ]
        return cls(stores=stores)


@dataclass(slots=True)
class Login(BaseData):
    token: str
    expired_at: datetime
    stores: list[Store]

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "Login":
        stores_data = data.get("stores", [])
        stores = [Store(**store) for store in stores_data]
        expires_at_str = data["expired_at"].replace("Z", "")
        expired_at = datetime.fromisoformat(expires_at_str)
        return cls(token=data["token"], expired_at=expired_at, stores=stores)





@dataclass(slots=True)
class ImageVariation:
    original: str
    sm: str
    md: str
    lg: str


@dataclass(slots=True)
class Image:
    id: str
    name: str
    type: int
    url: str
    order: int
    variations: ImageVariation


@dataclass(slots=True)
class VariantOption:
    name: str
    type: int
    values: list[str]


@dataclass(slots=True)
class Meta:
    title: str
    description: str
    images: list[str]  


@dataclass(slots=True)
class Product:
    id: str
    name: str
    slug: str
    public_url: str
    thumbnail: str
    description: str
    price: float
    compare_at_price: float
    cost_price: Optional[float]
    visibility: bool
    has_variants: bool
    variants_count: int
    variant_options: list[VariantOption]
    inventory: int
    track_inventory: bool
    you_save_amount: float
    meta: Meta
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[bool]
    images: list[Image]


@dataclass(slots=True)
class ProductList(BaseData):
    products: list[Product]

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> 'ProductList':
        def parse_image_variations(variations: dict[str, str]) -> ImageVariation:
            return ImageVariation(
                original=variations.get('original', ''),
                sm=variations.get('sm', ''),
                md=variations.get('md', ''),
                lg=variations.get('lg', '')
            )
        
        def parse_image(image_data: dict[str, Any]) -> Image:
            return Image(
                id=image_data['id'],
                name=image_data['name'],
                type=image_data['type'],
                url=image_data['url'],
                order=image_data['order'],
                variations=parse_image_variations(image_data.get('variations', {}))
            )
        
        def parse_variant_option(option_data: dict[str, Any]) -> VariantOption:
            return VariantOption(
                name=option_data['name'],
                type=option_data['type'],
                values=option_data.get('values', [])
            )
        
        def parse_meta(meta_data: dict[str, Any]) -> Meta:
            return Meta(
                title=meta_data['title'],
                description=meta_data['description'],
                images=meta_data.get('images', [])
            )

        def parse_product(product_data: dict[str, Any]) -> Product:
            return Product(
                id=product_data['id'],
                name=product_data['name'],
                slug=product_data['slug'],
                public_url=product_data['public_url'],
                thumbnail=product_data['thumbnail'],
                description=product_data['description'],
                price=product_data['price'],
                compare_at_price=product_data['compare_at_price'],
                cost_price=product_data.get('cost_price'),
                visibility=product_data['visibility'],
                has_variants=product_data['has_variants'],
                variants_count=product_data['variants_count'],
                variant_options=[parse_variant_option(option) for option in product_data.get('variant_options', [])],
                inventory=product_data['inventory'],
                track_inventory=product_data['track_inventory'],
                you_save_amount=product_data['you_save_amount'],
                meta=parse_meta(product_data['meta']),
                created_at=datetime.fromisoformat(product_data['created_at']),
                updated_at=datetime.fromisoformat(product_data['updated_at']),
                deleted_at=product_data.get('deleted_at'),
                images=[parse_image(img) for img in product_data.get('images', [])]
            )

        products_data = [parse_product(item) for item in data]
        return cls(products=products_data)
