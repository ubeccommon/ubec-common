"""
UBEC Protocol Web Interface - Main Application
================================================

REFACTORED: UI-only frontend that fetches data from api.ubec.network
EXTENDED: Now includes application submission handling with UI database

This module serves:
    - Public web pages (home, dashboard, about, protocol, stories)
    - Documentation guides
    - Application forms for beneficiaries
    - Admin dashboard for reviewing applications
    - Static assets

Data is fetched from the dedicated API gateway at api.ubec.network,
NOT directly from the backend. This ensures:
    - Single source of truth for all API data
    - Clean separation between UI and API
    - External developers use the same API as the frontend

Application data is stored in the UI-specific database (ubec_ui_interface)
which is separate from the main protocol database.

Architecture:
    bioregional.ubec.network (this service, port 8001)
        ↓ fetches data from
    api.ubec.network (API gateway, port 8002)
        ↓ proxies to
    Backend API (92.205.230.245:8000)

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""
from dotenv import load_dotenv
load_dotenv()  # Load .env before any other imports


import logging
import markdown
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from config.settings import settings
from utils.backend_client import get_backend_client, close_backend_client

# Import UI database connection
from database.ui_db_connection import init_db_pool, close_db_pool, check_db_health

# Import application routes
from routes.application_routes import router as application_router

# Import admin routes with graceful fallback
try:
    from routes.admin_routes import (
        router as admin_router,
        initialize_admin_service,
        shutdown_admin_service,
        get_admin_service
    )
    ADMIN_ROUTES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Admin routes not available: {e}")
    ADMIN_ROUTES_AVAILABLE = False
    admin_router = None
    get_admin_service = None

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========================================================================
# APPLICATION SETUP
# ========================================================================

app = FastAPI(
    title="UBEC Protocol Web Interface",
    description="Ubuntu Bioregional Economic Commons Protocol - Public Web Interface",
    version="1.0.0",
    # API docs disabled - use api.ubec.network for API documentation
    docs_url=None,
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Directory where guide markdown files are stored
GUIDES_DIR = Path("static/docs/guides")

# Include application routes
app.include_router(application_router)

# Include admin routes if available
if ADMIN_ROUTES_AVAILABLE and admin_router:
    app.include_router(admin_router)
    logger.info("Admin routes registered")

# ========================================================================
# LIFECYCLE EVENTS
# ========================================================================

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("Starting UBEC Protocol Web Interface")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"API Source: {settings.BACKEND_API_URL}")
    
    # Initialize UI database pool
    db_pool = None
    try:
        await init_db_pool()
        logger.info("UI Database pool initialized")
        
        # Try to get the pool for admin service
        try:
            from database.ui_db_connection import get_db_pool
            db_pool = await get_db_pool()
        except (ImportError, AttributeError):
            logger.debug("get_db_pool not available in ui_db_connection")
    except Exception as e:
        logger.error(f"Failed to initialize UI database: {e}")
        logger.warning("Application submissions will not work until database is available")
    
    # Initialize admin service if available
    if ADMIN_ROUTES_AVAILABLE:
        try:
            await initialize_admin_service(db_pool)
            logger.info("Admin service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize admin service: {e}")
            logger.warning("Admin dashboard will use mock data")
    
    logger.info("Web interface ready on port 8001")
    logger.info("NOTE: API moved to api.ubec.network")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down UBEC Protocol Web Interface...")
    await close_backend_client()
    
    # Shutdown admin service if available
    if ADMIN_ROUTES_AVAILABLE:
        try:
            await shutdown_admin_service()
            logger.info("Admin service shutdown complete")
        except Exception as e:
            logger.warning(f"Error shutting down admin service: {e}")
    
    await close_db_pool()
    logger.info("Shutdown complete")

# ========================================================================
# APPLICATION FORM PAGES
# ========================================================================

@app.get("/apply", response_class=HTMLResponse, name="apply")
async def apply_landing(request: Request):
    """Application landing page with pathway options."""
    return templates.TemplateResponse("apply.html", {"request": request, "page": "apply"})


@app.get("/apply/farmer", response_class=HTMLResponse, name="apply_farmer")
async def apply_farmer(request: Request):
    """Farmer application form."""
    return templates.TemplateResponse("apply-farmer.html", {"request": request, "page": "apply"})


@app.get("/apply/community", response_class=HTMLResponse, name="apply_community")
async def apply_community(request: Request):
    """Community application form."""
    return templates.TemplateResponse("apply-community.html", {"request": request, "page": "apply"})


@app.get("/apply/activator", response_class=HTMLResponse, name="apply_activator")
async def apply_activator(request: Request):
    """Community activator application form."""
    return templates.TemplateResponse("apply-activator.html", {"request": request, "page": "apply"})


@app.get("/apply/livinglab", response_class=HTMLResponse, name="apply_livinglab")
async def apply_livinglab(request: Request):
    """Living lab application form."""
    return templates.TemplateResponse("apply-livinglab.html", {"request": request, "page": "apply"})


@app.get("/apply/success", response_class=HTMLResponse, name="apply_success")
async def apply_success(request: Request, ref: str = None, type: str = None):
    """Application submission success page."""
    return templates.TemplateResponse("apply-success.html", {
        "request": request,
        "page": "apply",
        "reference_number": ref,
        "application_type": type
    })

# ========================================================================
# PUBLIC WEB PAGES
# ========================================================================

@app.get("/", response_class=HTMLResponse, name="home")
async def home(request: Request):
    """Home page with live token and network data."""
    context = {
        "request": request,
        "page": "home",
        "tokens": [],
        "network": {
            "participants": 0,
            "bioregions": 0,
            "transactions": 0,
            "health": "unknown"
        },
        "total_holders": 0
    }
    
    try:
        client = await get_backend_client()
        
        # Fetch token data
        try:
            tokens_response = await client.get_all_tokens()
            if tokens_response and isinstance(tokens_response, list):
                context["tokens"] = tokens_response
                context["total_holders"] = sum(
                    t.get('holder_count', 0) for t in context["tokens"]
                )
                logger.info(f"Loaded {len(context['tokens'])} tokens")
        except Exception as e:
            logger.warning(f"Could not fetch tokens: {e}")
        
        # Fetch network status
        try:
            network_response = await client.get_network_status()
            if network_response and isinstance(network_response, dict):
                context["network"] = network_response.get('network', context["network"])
                logger.info(f"Network: {context['network'].get('participants', 0)} participants")
        except Exception as e:
            logger.warning(f"Could not fetch network status: {e}")
            
    except Exception as e:
        logger.error(f"Error fetching home page data: {e}")
    
    return templates.TemplateResponse("home.html", context)


@app.get("/stories", response_class=HTMLResponse, name="stories")
async def stories(request: Request):
    """Community stories page."""
    return templates.TemplateResponse("stories.html", {"request": request, "page": "stories"})


@app.get("/about", response_class=HTMLResponse, name="about")
async def about(request: Request):
    """About page."""
    return templates.TemplateResponse("about.html", {"request": request, "page": "about"})


@app.get("/protocol", response_class=HTMLResponse, name="protocol")
async def protocol(request: Request):
    """Protocol documentation page."""
    try:
        return templates.TemplateResponse("protocol.html", {"request": request, "page": "protocol"})
    except:
        return HTMLResponse(
            content="""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Protocol - UBEC</title></head>
            <body><h1>Protocol Overview Unavailable</h1><p><a href="/">Return to Home</a></p></body></html>""",
            status_code=500
        )


@app.get("/dashboard", response_class=HTMLResponse, name="dashboard")
async def dashboard(request: Request):
    """Live Dashboard with network metrics."""
    context = {
        "request": request,
        "network_status": {
            'active_participants': 0,
            'total_transactions_24h': 0,
            'bioregions_count': 0,
            'average_ubuntu_score': 0.0,
            'last_block_time': 'Unavailable'
        },
        "holonic_scores": None,
        "recent_transactions": [],
        "distribution_stats": None,
        "token_audit": None,
        "liquidity_pools": None,
        "ecoregions": None,
        "watersheds": None,
        "page": "dashboard"
    }
    
    try:
        client = await get_backend_client()
        
        # ============================================================
        # NETWORK STATUS
        # ============================================================
        try:
            raw_network_status = await client.get_network_status()
            if raw_network_status and isinstance(raw_network_status, dict):
                network_data = raw_network_status.get('network', {})
                
                context["network_status"] = {
                    'active_participants': network_data.get('participants', 0),
                    'total_transactions_24h': network_data.get('transactions', 0),
                    'bioregions_count': network_data.get('bioregions', 0),
                    'average_ubuntu_score': network_data.get('ubuntu_alignment', 0.0),
                    'last_block_time': raw_network_status.get('timestamp', 'Unavailable')
                }
                logger.info(f"Network status loaded: {context['network_status']['active_participants']} participants")
        except Exception as e:
            logger.warning(f"Could not fetch network status: {e}")
        
        # ============================================================
        # HOLONIC SCORES
        # ============================================================
        try:
            raw_holonic = await client.get_holonic_scores()
            if raw_holonic and isinstance(raw_holonic, dict):
                # Transform API response to template-expected format
                principles = raw_holonic.get('ubuntu_principles', {})
                
                # Extract averages from nested structure
                diversity = principles.get('diversity', {}).get('average', 0) or 0
                reciprocity = principles.get('reciprocity', {}).get('average', 0) or 0
                mutualism = principles.get('mutualism', {}).get('average', 0) or 0
                regeneration = principles.get('regeneration', {}).get('average', 0) or 0
                
                # Calculate overall network health
                overall = (diversity + reciprocity + mutualism + regeneration) / 4
                
                # Build template-ready context
                context["holonic_scores"] = {
                    "overall_network_health": overall,
                    "autonomy_integration": diversity,
                    "ubuntu_alignment": diversity,
                    "reciprocity_health": reciprocity,
                    "mutualism_capacity": mutualism,
                    "regeneration_impact": regeneration,
                    "account_count": raw_holonic.get('account_count', 0)
                }
                logger.info(f"Holonic scores loaded: overall={overall:.2%}, diversity={diversity:.2%}")
            else:
                context["holonic_scores"] = None
        except Exception as e:
            logger.warning(f"Could not fetch holonic scores: {e}")
        
        # ============================================================
        # RECENT TRANSACTIONS
        # ============================================================
        try:
            raw_transactions = await client.get_recent_transactions(limit=10)
            # Handle both response formats: list directly or {"transactions": [...]}
            if raw_transactions:
                if isinstance(raw_transactions, list):
                    context["recent_transactions"] = raw_transactions
                    logger.info(f"Loaded {len(raw_transactions)} recent transactions (list format)")
                elif isinstance(raw_transactions, dict):
                    # Pass the full dict - template handles extraction
                    context["recent_transactions"] = raw_transactions
                    tx_count = len(raw_transactions.get('transactions', []))
                    logger.info(f"Loaded {tx_count} recent transactions (dict format)")
        except Exception as e:
            logger.warning(f"Could not fetch recent transactions: {e}")
        
        # ============================================================
        # DISTRIBUTION STATS
        # ============================================================
        try:
            raw_distribution = await client.get_distribution_stats()
            if raw_distribution and isinstance(raw_distribution, dict):
                context["distribution_stats"] = raw_distribution
                logger.info("Distribution stats loaded")
        except Exception as e:
            logger.warning(f"Could not fetch distribution stats: {e}")
        
        # ============================================================
        # TOKEN AUDIT
        # ============================================================
        try:
            raw_audit = await client.get_token_audit()
            if raw_audit and isinstance(raw_audit, dict):
                context["token_audit"] = raw_audit
                logger.info("Token audit loaded")
        except Exception as e:
            logger.warning(f"Could not fetch token audit: {e}")
        
        # ============================================================
        # LIQUIDITY POOLS
        # ============================================================
        try:
            raw_pools = await client.get_liquidity_pools()
            if raw_pools and isinstance(raw_pools, dict):
                context["liquidity_pools"] = raw_pools
                logger.info("Liquidity pools loaded")
        except Exception as e:
            logger.warning(f"Could not fetch liquidity pools: {e}")
        
        # ============================================================
        # ECOREGIONS
        # ============================================================
        try:
            raw_ecoregions = await client.get_ecoregions(limit=10)
            if raw_ecoregions and isinstance(raw_ecoregions, dict):
                ecoregions_list = raw_ecoregions.get('ecoregions', [])
                total_ecoregions = raw_ecoregions.get('count', len(ecoregions_list))
                transformed_ecoregions = []
                for eco in ecoregions_list:
                    transformed_ecoregions.append({
                        'eco_id': eco.get('eco_code', ''),
                        'name': eco.get('eco_name', ''),
                        'biome': eco.get('biome_name', ''),
                        'realm': eco.get('realm', ''),
                        'biome_num': eco.get('biome_num', 0)
                    })
                biomes = set(e['biome'] for e in transformed_ecoregions if e['biome'])
                realms = set(e['realm'] for e in transformed_ecoregions if e['realm'])
                context["ecoregions"] = {
                    'total_ecoregions': total_ecoregions,
                    'biome_types': len(biomes),
                    'biogeographic_realms': len(realms),
                    'ecoregions': transformed_ecoregions,
                    'biomes': sorted(list(biomes))
                }
                logger.info(f"Loaded {len(transformed_ecoregions)} ecoregions")
            else:
                context["ecoregions"] = None
        except Exception as e:
            logger.warning(f"Could not fetch ecoregions: {e}")
            context["ecoregions"] = None
        
        # ============================================================
        # WATERSHEDS
        # ============================================================
        try:
            raw_watersheds = await client.get_watersheds(limit=10)
            if raw_watersheds and isinstance(raw_watersheds, dict):
                watersheds_list = raw_watersheds.get('watersheds', [])
                total_watersheds = raw_watersheds.get('count', len(watersheds_list))
                transformed_watersheds = []
                for ws in watersheds_list:
                    area_acres = ws.get('area_acres', 0) or 0
                    area_sqkm = area_acres * 0.00404686
                    transformed_watersheds.append({
                        'feow_id': ws.get('huc12', ''),
                        'name': ws.get('name', ''),
                        'area_sqkm': area_sqkm
                    })
                total_area = sum(w['area_sqkm'] for w in transformed_watersheds)
                context["watersheds"] = {
                    'total_count': total_watersheds,
                    'total_area_sqkm': total_area,
                    'major_watersheds': transformed_watersheds,
                    'average_area': total_area / len(transformed_watersheds) if transformed_watersheds else 0
                }
                logger.info(f"Loaded {len(transformed_watersheds)} watersheds")
            else:
                context["watersheds"] = None
        except Exception as e:
            logger.warning(f"Could not fetch watersheds: {e}")
            context["watersheds"] = None
        
        return templates.TemplateResponse("dashboard.html", context)
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}", exc_info=True)
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "status_code": 500,
                "error_message": "The backend service is unavailable at the moment. Please try again in a moment.",
                "page": "error"
            }
        )

# ========================================================================
# DOCUMENTATION PAGES
# ========================================================================

@app.get("/docs", response_class=HTMLResponse, name="docs")
async def docs(request: Request):
    """Documentation landing page."""
    return templates.TemplateResponse("docs.html", {"request": request, "page": "docs"})


@app.get("/docs/guides/", response_class=HTMLResponse, name="guides_index")
async def guides_index(request: Request):
    """Display index of all available guides."""
    try:
        guides = []
        if GUIDES_DIR.exists():
            for file in GUIDES_DIR.glob("*.md"):
                title = file.stem.replace("-", " ").replace("_", " ").title()
                slug = file.stem
                guides.append({
                    "title": title,
                    "slug": slug,
                    "filename": file.name
                })
        
        guides.sort(key=lambda x: x['title'])
        
        return templates.TemplateResponse(
            "guides_index.html",
            {
                "request": request,
                "guides": guides,
                "page": "guides"
            }
        )
    except Exception as e:
        logger.error(f"Error loading guides index: {e}")
        raise HTTPException(status_code=500, detail="Unable to load guides")


@app.get("/docs/guides/{guide_slug}", response_class=HTMLResponse, name="guide_detail")
async def guide_detail(request: Request, guide_slug: str):
    """Display a specific guide document."""
    try:
        guide_file = GUIDES_DIR / f"{guide_slug}.md"
        
        if not guide_file.exists():
            logger.warning(f"Guide not found: {guide_slug}")
            raise HTTPException(status_code=404, detail=f"Guide '{guide_slug}' not found")
        
        with open(guide_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        html_content = markdown.markdown(
            markdown_content,
            extensions=['extra', 'toc', 'codehilite', 'fenced_code']
        )
        
        title = guide_slug.replace("-", " ").title()
        if markdown_content.startswith('# '):
            title = markdown_content.split('\n')[0].replace('# ', '')
        
        return templates.TemplateResponse(
            "guide_detail.html",
            {
                "request": request,
                "title": title,
                "content": html_content,
                "guide_slug": guide_slug,
                "page": "guides"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading guide {guide_slug}: {e}")
        raise HTTPException(status_code=500, detail="Unable to load guide")


@app.get("/docs/guides/{guide_slug}/raw", response_class=FileResponse, name="guide_raw")
async def guide_raw(guide_slug: str):
    """Download raw markdown file."""
    try:
        guide_file = GUIDES_DIR / f"{guide_slug}.md"
        
        if not guide_file.exists():
            raise HTTPException(status_code=404, detail=f"Guide '{guide_slug}' not found")
        
        return FileResponse(
            path=guide_file,
            media_type='text/markdown',
            filename=f"{guide_slug}.md"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading guide {guide_slug}: {e}")
        raise HTTPException(status_code=500, detail="Unable to download guide")

# ========================================================================
# HEALTH CHECK - Service Registry Pattern
# ========================================================================

@app.get("/health", response_class=JSONResponse)
async def health_check():
    """
    Health check endpoint with comprehensive service status.
    
    Follows the standardized service registry pattern:
    - Checks all registered services
    - Aggregates overall health status
    - Returns detailed service-level status
    """
    # Track overall health - starts healthy, degrades if any service fails
    overall_healthy = True
    
    # Build services status dictionary
    services = {}
    
    # Check UI database health
    try:
        ui_db_health = await check_db_health()
        services["ui_database"] = {
            "status": "healthy" if ui_db_health.get("status") == "healthy" else "unhealthy",
            "details": ui_db_health
        }
        if ui_db_health.get("status") != "healthy":
            overall_healthy = False
    except Exception as e:
        logger.warning(f"UI database health check failed: {e}")
        services["ui_database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_healthy = False
    
    # Check admin service if available
    if ADMIN_ROUTES_AVAILABLE and get_admin_service is not None:
        try:
            admin_svc = await get_admin_service()
            if admin_svc and admin_svc.is_initialized():
                admin_health = await admin_svc.health_check()
                services["admin_service"] = {
                    "status": "healthy" if admin_health.get("initialized") else "degraded",
                    "version": admin_health.get("version", "unknown"),
                    "active_sessions": admin_health.get("active_sessions", 0),
                    "database": admin_health.get("database", "unknown")
                }
                if not admin_health.get("initialized"):
                    overall_healthy = False
            else:
                services["admin_service"] = {
                    "status": "not_initialized",
                    "message": "Admin service not yet initialized"
                }
        except Exception as e:
            logger.warning(f"Admin service health check failed: {e}")
            services["admin_service"] = {
                "status": "unavailable",
                "error": str(e)
            }
    else:
        services["admin_service"] = {
            "status": "not_installed",
            "message": "Admin routes module not available"
        }
    
    # Determine overall status
    if overall_healthy:
        overall_status = "healthy"
    elif any(s.get("status") == "healthy" for s in services.values()):
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"
    
    return {
        "status": overall_status,
        "service": "ubec-web-interface",
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "api_note": "API moved to api.ubec.network",
        "services": services
    }

# ========================================================================
# ERROR HANDLERS
# ========================================================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 404,
            "error_message": "The requested page could not be found.",
            "page": "error"
        },
        status_code=404
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    logger.error(f"Internal server error: {exc}")
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 500,
            "error_message": "An internal server error occurred. Please try again later.",
            "page": "error"
        },
        status_code=500
    )
