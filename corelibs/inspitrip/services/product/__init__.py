from .price_engine_request import PriceEngineRequest
from .coupon_request import CouponRequest
from .product_request import ProductRequest


class Product(PriceEngineRequest, CouponRequest, ProductRequest):
    """
    Add class actions for product here
    """
    pass
