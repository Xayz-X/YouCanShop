# import asyncio
from .http import HTTPClient
import entities


class StoreClient:
    __slots__ = "_http"
    
    def __init__(self) -> None:
        self._http: HTTPClient = HTTPClient()

    def set_token(self, token: str) -> None:
        """
        Set store Bearer token for all request.
        
        Parameters
        ----------
        token : str
            Active token of the shop.
            
        Example
        -------
        >>> set_token(token="test token") # Dont need to mention the token type. (By default it use Bearer token type)
        """
        self._http.token = token


    async def login(self, email: str, password: str) -> entities.Shop:
        """
        Login to store with email and password.

        Parameters
        ----------
        email : `str`
            Email address of your store.
        password : str
            Password of your store.

        Example
        -------
        >>> await login(email="test@mgail.com", password="test")
        """
        response = await self._http._login(email=email, password=password)
        return entities.Shop.from_json(data=response)
    
    


    # async def get_stores(self) -> entities.StoreList:
    #     """Get all list of store regardless of active and inactive"""
    #     response = await self._http._stores()
    #     return entities.StoreList.from_json(response)

    # async def get_products(self) -> entities.ProductList:
    #     """Get a full list of products"""
    #     response = await self._http._get_products()
    #     return entities.ProductList.from_json(response)

    # async def search_orders(self, search_term: str) -> None:
    #     response = await self._http._search_orders(search_value=search_term)
    #     import json
    #     print(json.dumps(response, indent=4))

    # async def order_fulfill(self, order_id: str, seller_note: str, tracking_number: str = None) -> None:
    #     """Fulfill any order by the order ID, Not ref no."""
    #     response = await self._http._order_fulfill(order_id=order_id,
    #                                                 seller_note=seller_note,
    #                                                 tracking_number=tracking_number)
