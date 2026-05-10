from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.export import geojson_builder, pdf_builder

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/geojson")
def choropleth_geojson(indicator_code: str, year: int = 2022, db: Session = Depends(get_db)):
    """
    GeoJSON FeatureCollection (Point) עם ערכי מדד לכל רשות שיש לה קואורדינטות.
    GET /api/v1/export/geojson?indicator_code=POP_TOTAL&year=2022
    """
    return JSONResponse(content=geojson_builder.build_choropleth_geojson(db, indicator_code, year))


@router.get("/pdf/{municipality_id}")
def download_pdf(municipality_id: int, year: int = 2022, db: Session = Depends(get_db)):
    """
    דוח PDF בעברית לרשות ושנה.
    GET /api/v1/export/pdf/504?year=2022
    """
    try:
        pdf_bytes = pdf_builder.build_pdf(db, municipality_id, year)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=report_{municipality_id}_{year}.pdf"
        },
    )
