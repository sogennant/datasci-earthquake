"""Router to handle liquefaction-related API endpoints"""

from fastapi import Depends, HTTPException, APIRouter, Query
from typing import Optional
from ..tags import Tags
from sqlalchemy.orm import Session
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from backend.database.session import get_db
from ..schemas.liquefaction_schemas import (
    LiquefactionFeature,
    LiquefactionFeatureCollection,
    IsInLiquefactionZoneView,
)
from backend.api.models.liquefaction_zones import LiquefactionZone
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/liquefaction-zones",
    tags=[Tags.LIQUEFACTION],
)


@router.get("", response_model=LiquefactionFeatureCollection)
async def get_liquefaction_zones(db: Session = Depends(get_db)):
    """
    Retrieve all liquefaction zones from the database.

    Args:
        db (Session): The database session dependency.

    Returns:
        LiquefactionFeatureCollection: A collection of all liquefaction zones as GeoJSON Features.

    Raises:
        HTTPException: If no zones are found (404 error).
    """
    # Query the database for all liquefaction zones
    liquefaction_zones = db.query(LiquefactionZone).all()

    # If no zones are found, raise a 404 error
    if not liquefaction_zones:
        raise HTTPException(status_code=404, detail="No liquefaction zones found")

    features = [
        LiquefactionFeature.from_sqlalchemy_model(zone) for zone in liquefaction_zones
    ]
    return LiquefactionFeatureCollection(type="FeatureCollection", features=features)


@router.get("/is-in-liquefaction-zone", response_model=IsInLiquefactionZoneView)
async def is_in_liquefaction_zone(
    lon: Optional[float] = Query(None),
    lat: Optional[float] = Query(None),
    ping: bool = False,
    db: Session = Depends(get_db),
):
    """
    Check if a point is in a liquefaction zone.

    Args:
        lon (float): Longitude of the point.
        lat (float): Latitude of the point.
        ping (bool): Optional ping parameter, used to reduce cold starts.
        db (Session): The database session dependency.

    Returns:
        IsInLiquefactionZoneView containing:
            - exists: True if point is in a liquefaction zone
            - last_updated: Timestamp of last update if exists, None otherwise

         If `ping=true` is passed, skips DB call and returns a dummy IsInLiquefactionZoneView(exists=False, last_updated=None) instance.
    """
    if ping:
        logger.info(f"Pinging the is-in-liquefaction-zone endpoint")
        return IsInLiquefactionZoneView(exists=False, last_updated=None)  # skip DB call

    if lon is None or lat is None:
        logger.warning("Missing coordinates in non-ping request")
        raise HTTPException(
            status_code=400,
            detail="Both 'lon' and 'lat' must be provided unless ping=true",
        )

    logger.info(f"Checking liquefaction zone for coordinates: lon={lon}, lat={lat}")

    try:
        point = from_shape(Point(lon, lat), srid=4326)
        zone = (
            db.query(LiquefactionZone)
            .filter(LiquefactionZone.geometry.ST_Intersects(point))
            .first()
        )
        exists = zone is not None
        last_updated = zone.update_timestamp if zone else None

        logger.info(
            f"Liquefaction zone check result for coordinates: lon={lon}, lat={lat} - "
            f"exists: {exists}, "
            f"last_updated: {last_updated}"
        )

        return IsInLiquefactionZoneView(exists=exists, last_updated=last_updated)

    except Exception as e:
        logger.error(
            f"Error checking liquefaction zone status for coordinates: lon={lon}, lat={lat}, "
            f"error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error checking liquefaction zone status for coordinates: lon={lon}, lat={lat}, "
            f"error: {str(e)}",
        )
