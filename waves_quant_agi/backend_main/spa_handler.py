"""
SPA (Single Page Application) Handler for FastAPI
Handles serving React app and fallback routes
"""
import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.responses import HTMLResponse

def setup_spa_handler(app: FastAPI, static_dir: str = "frontend/dist"):
    """
    Setup SPA handler for React app
    
    Args:
        app: FastAPI app instance
        static_dir: Directory containing the built React app
    """
    
    # Check if static directory exists
    static_path = Path(static_dir)
    if not static_path.exists():
        print(f"Warning: Static directory {static_dir} not found. SPA handler not configured.")
        return
    
    # Mount static files
    app.mount("/static", StaticFiles(directory=str(static_path / "static")), name="static")
    
    # Serve other static files (favicon, robots.txt, etc.)
    @app.get("/favicon.ico")
    async def favicon():
        favicon_path = static_path / "favicon.ico"
        if favicon_path.exists():
            return FileResponse(str(favicon_path))
        return None
    
    @app.get("/robots.txt")
    async def robots():
        robots_path = static_path / "robots.txt"
        if robots_path.exists():
            return FileResponse(str(robots_path))
        return None
    
    # SPA fallback - serve index.html for all unknown routes
    @app.get("/{full_path:path}")
    async def spa_fallback(request: Request, full_path: str):
        # Don't handle API routes
        if full_path.startswith("api/"):
            return None
        
        # Don't handle static files
        if full_path.startswith("static/"):
            return None
        
        # Serve index.html for all other routes
        index_path = static_path / "index.html"
        if index_path.exists():
            return FileResponse(
                str(index_path),
                media_type="text/html"
            )
        
        # Fallback HTML response if index.html doesn't exist
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Waves Quant Engine</title>
        </head>
        <body>
            <h1>Waves Quant Engine</h1>
            <p>React app not built. Run 'npm run build' to build the frontend.</p>
        </body>
        </html>
        """)

def create_spa_app(static_dir: str = "frontend/dist") -> FastAPI:
    """
    Create a FastAPI app with SPA handler configured
    
    Args:
        static_dir: Directory containing the built React app
    
    Returns:
        FastAPI app with SPA handler
    """
    app = FastAPI(title="Waves Quant Engine API")
    setup_spa_handler(app, static_dir)
    return app 