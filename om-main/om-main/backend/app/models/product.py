from fastapi import APIRouter, HTTPException, UploadFile, File
from langfuse import observe
from app.services.product_service import ProductService
import os
import httpx
 
@router.post("/admin/products/upload")
@observe(name="upload_inventory_excel")
async def upload_inventory(file: UploadFile = File(...)):
    """Accepts an Excel file from the admin dashboard to update inventory."""
    try:
        content = await file.read()
        result_message = service.update_inventory_from_excel(content)
        
        if "Error:" in result_message or "Failed" in result_message:
            return {"success": False, "message": result_message}
            
        return {"success": True, "message": result_message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))