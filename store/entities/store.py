from typing import Any
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(slots=True)
class StoreSwitch:
    id: str
    token: str
    token_type: str
    expires_at: str

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> 'StoreSwitch':
        ...
        return cls(
            
        )

    @property
    def token_expires_timestamp(self) -> int:
        expiry_time = datetime.fromisoformat(
            self.expires_at[:-1]
        )  # Remove 'Z' and parse
        return int(expiry_time.replace(tzinfo=timezone.utc).timestamp())



@dataclass(slots=True)
class Store:
    id: str
    slug: str
    is_active: bool
    is_email_verified: bool


@dataclass(slots=True)
class Shop:
    token: str
    token_type: str
    is_staff: bool
    expires_at: str
    stores: list[Store] # if there is no store it might be an empty list 

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "Shop":
        stores = [
            Store(
                id=store["store_id"],
                slug=store["slug"],
                is_active=store["is_active"],
                is_email_verified=store["is_email_verified"],
            )
            for store in data.get("stores")
        ]
        return cls(
            token=data["token"],
            token_type=data["token_type"],
            is_staff=data["is_staff"],
            expires_at=data["expired_at"],
            stores=stores or [],
        )

    @property
    def token_expires_timestamp(self) -> int:
        expiry_time = datetime.fromisoformat(
            self.expires_at[:-1]
        )  # Remove 'Z' and parse
        return int(expiry_time.replace(tzinfo=timezone.utc).timestamp())

    @property
    def total_stores(self) -> int:
        return len(self.stores)

    @property
    def total_active_stores(self) -> int:
        return len(s for s in self.stores if s.is_active)

    @property
    def total_verified_stores(self) -> int:
        return len(s for s in self.stores if s.is_email_verified)
