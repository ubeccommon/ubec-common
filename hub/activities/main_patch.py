# ── Patch for /srv/ubec/hub/main.py ──────────────────────────────────────────
# Add these two lines to the existing main.py alongside the auth router import
# and include call. Do not replace the file — only add these lines.
#
# 1. Near the top, after:
#        from auth import router as auth_router
#    Add:
#        from activities import router as activities_router
#
# 2. After:
#        app.include_router(auth_router)
#    Add:
#        app.include_router(activities_router)
#
# That is the complete change required. The activities module uses
# auth.database.get_db and auth.dependencies, so no new database
# wiring is needed.
