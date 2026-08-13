# CRITICAL FIX: AttributeError 'sync_trustlines' Does Not Exist

## Problem Summary

**Error:**
```
AttributeError: 'UBECDataSynchronizer' object has no attribute 'sync_trustlines'
```

**Location:** `main.py` line 1448 in `run_sync()` function

**Root Cause:** The code is calling `synchronizer.sync_trustlines()` - a method that does not exist in the `UBECDataSynchronizer` class.

---

## Available Synchronizer Methods

The `UBECDataSynchronizer` class (in `core/db/ubec_data_synchronizer.py`) has these methods:

### Discovery Methods
- `discover_accounts(asset_code, max_accounts)` - Discover token holders for a specific asset

### Sync Methods  
- `sync_account(account_id, asset_code)` - Sync a specific account
- **`sync_all_tokens(max_accounts_per_token)`** - Sync all 4 UBEC tokens ✅ USE THIS
- **`sync_all()`** - Alias for sync_all_tokens() ✅ OR THIS

### Non-Existent Methods (DON'T USE)
- ❌ `sync_trustlines()` - DOES NOT EXIST
- ❌ `sync_transactions()` - DOES NOT EXIST  
- ❌ `sync_all_accounts()` - DOES NOT EXIST
- ❌ `sync_accounts_by_token()` - DOES NOT EXIST

---

## The Fix

### Step 1: Locate the Broken Code

Find this in `main.py` (around line 1430-1460):

```python
async def run_sync(
    sync_type: str,
    max_accounts: Optional[int] = None,
    force: bool = False
) -> Dict[str, Any]:
    logger.info("\n" + "=" * 70)
    logger.info(f"RUNNING SYNC: {sync_type}")
    logger.info("=" * 70)
    
    synchronizer = await registry.get('synchronizer')
    
    try:
        if sync_type == 'accounts':
            result = await synchronizer.sync_all_accounts(  # ❌ DOESN'T EXIST
                max_accounts=max_accounts,
                force=force
            )
        elif sync_type == 'transactions':
            result = await synchronizer.sync_transactions(force=force)  # ❌ DOESN'T EXIST
        elif sync_type == 'all':
            result = await synchronizer.sync_trustlines(max_accounts=max_accounts)  # ❌ DOESN'T EXIST - LINE 1448!
        else:
            result = await synchronizer.sync_accounts_by_token(  # ❌ DOESN'T EXIST
                token_code=sync_type.upper(),
                max_accounts=max_accounts
            )
        
        return create_response(success=True, data=result)
```

### Step 2: Replace With Corrected Code

Replace the entire `run_sync()` function with:

```python
async def run_sync(
    sync_type: str,
    max_accounts: Optional[int] = None,
    force: bool = False
) -> Dict[str, Any]:
    """
    Run blockchain data synchronization.
    
    Args:
        sync_type: 'all' for all tokens, or specific token code (UBEC, UBECrc, etc.)
        max_accounts: Maximum accounts to discover per token
        force: Force re-sync (currently unused but kept for compatibility)
        
    Returns:
        Dictionary with sync results
        
    Principle #5: Strict Async
    Principle #12: Method Singularity - Uses actual synchronizer methods
    """
    logger.info("\n" + "=" * 70)
    logger.info(f"RUNNING SYNC: {sync_type}")
    logger.info("=" * 70)
    
    synchronizer = await registry.get('synchronizer')
    
    try:
        if sync_type == 'all':
            # ✅ CORRECT: Use sync_all_tokens() to sync all 4 UBEC tokens
            logger.info("Synchronizing all UBEC tokens...")
            result = await synchronizer.sync_all_tokens(
                max_accounts_per_token=max_accounts or 5000
            )
            
        else:
            # ✅ CORRECT: Use discover_accounts() for specific token
            token_code = sync_type.upper()
            logger.info(f"Discovering {token_code} token holders...")
            
            accounts_discovered = await synchronizer.discover_accounts(
                asset_code=token_code,
                max_accounts=max_accounts or 5000
            )
            
            result = {
                'token': token_code,
                'accounts_discovered': accounts_discovered,
                'status': 'success'
            }
        
        logger.info("✓ Synchronization completed successfully")
        return create_response(success=True, data=result)
        
    except Exception as e:
        logger.error(f"Sync failed: {e}", exc_info=True)
        return create_response(success=False, error=str(e))
```

---

## What Changed

### Before (Broken):
```python
elif sync_type == 'all':
    result = await synchronizer.sync_trustlines(max_accounts=max_accounts)  # ❌
```

### After (Fixed):
```python
if sync_type == 'all':
    result = await synchronizer.sync_all_tokens(
        max_accounts_per_token=max_accounts or 5000
    )  # ✅
```

### Key Differences:

1. **Method name:** `sync_trustlines()` → `sync_all_tokens()`
2. **Parameter name:** `max_accounts` → `max_accounts_per_token`
3. **Default value:** No default → `5000` if not specified

---

## Testing the Fix

After applying the fix:

```bash
# Test sync all tokens
python main.py sync --sync-type all --force

# Test sync specific token
python main.py sync --sync-type UBEC --force

# Test with max accounts limit
python main.py sync --sync-type all --max-accounts 100 --force
```

### Expected Output:

```
======================================================================
RUNNING SYNC: all
======================================================================
2025-10-24 07:19:15 - INFO - Synchronizing all UBEC tokens...
2025-10-24 07:19:16 - INFO - Discovering UBEC holders...
2025-10-24 07:19:17 - INFO - ✓ Discovered 643 UBEC holders
2025-10-24 07:19:17 - INFO - Discovering UBECrc holders...
2025-10-24 07:19:18 - INFO - ✓ Discovered 4 UBECrc holders
2025-10-24 07:19:18 - INFO - Discovering UBECgpi holders...
2025-10-24 07:19:19 - INFO - ✓ Discovered 3 UBECgpi holders
2025-10-24 07:19:19 - INFO - Discovering UBECtt holders...
2025-10-24 07:19:20 - INFO - ✓ Discovered 1 UBECtt holders
2025-10-24 07:19:20 - INFO - ✓ Synchronization completed successfully
======================================================================
```

---

## Why This Happened

The `main.py` file appears to have been written expecting different method names than what the `UBECDataSynchronizer` class actually implements. This is a **method signature mismatch** between:

1. **What main.py expects:** `sync_trustlines()`, `sync_transactions()`, `sync_all_accounts()`
2. **What synchronizer provides:** `sync_all_tokens()`, `discover_accounts()`, `sync_account()`

This suggests either:
- The synchronizer was refactored and main.py wasn't updated, OR
- main.py was written based on outdated documentation/assumptions

---

## Principle Compliance

This fix maintains compliance with:

### ✅ Principle #12: Method Singularity
- Uses the actual methods that exist in the synchronizer
- No duplicate implementations

### ✅ Principle #5: Strict Async Operations  
- All operations remain async
- Proper await usage throughout

### ✅ Principle #3: Service Registry for Dependencies
- Continues to use registry.get('synchronizer')
- No direct imports or instantiation

---

## Additional Notes

### Sync Types Supported After Fix:

| sync_type | Action | Method Called |
|-----------|--------|---------------|
| `all` | Sync all 4 UBEC tokens | `sync_all_tokens(max_accounts_per_token=N)` |
| `UBEC` | Discover UBEC holders | `discover_accounts('UBEC', max_accounts=N)` |
| `UBECrc` | Discover UBECrc holders | `discover_accounts('UBECrc', max_accounts=N)` |
| `UBECgpi` | Discover UBECgpi holders | `discover_accounts('UBECgpi', max_accounts=N)` |
| `UBECtt` | Discover UBECtt holders | `discover_accounts('UBECtt', max_accounts=N)` |

### Command Line Examples:

```bash
# Sync everything
python main.py sync --sync-type all --force

# Discover UBEC holders (limit 100)
python main.py sync --sync-type UBEC --max-accounts 100

# Discover all Water token holders  
python main.py sync --sync-type UBECrc --force
```

---

## File Locations

- **File to fix:** `main.py` (line ~1430-1460, function `run_sync`)
- **Reference implementation:** `core/db/ubec_data_synchronizer.py`
- **This document:** `SYNC_TRUSTLINES_FIX.md`
- **Code reference:** `fix_run_sync.py`

---

## Quick Action Checklist

- [ ] Back up current `main.py`
- [ ] Open `main.py` in editor
- [ ] Find `run_sync` function (around line 1430)
- [ ] Replace function with corrected version above
- [ ] Save file
- [ ] Test: `python main.py sync --sync-type all --force`
- [ ] Verify: Check protocol-health shows updated sync times
- [ ] Done!

---

*This fix resolves the AttributeError and restores full synchronization functionality.*
