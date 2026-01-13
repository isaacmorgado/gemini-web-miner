"""
Crawl4AI Authentication Examples
Real-world examples extracted from the crawl4ai repository

Repository: https://github.com/unclecode/crawl4ai
"""

import asyncio
import base64
import tempfile
import os
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig


# ==============================================================================
# EXAMPLE 1: Form-Based Login (C4A Script)
# ==============================================================================


async def example_form_login_c4a_script():
    """Login using C4A Script (recommended for form-based auth)"""

    login_script = """
    # Define reusable login procedure
    PROC login
      CLICK `#username`
      TYPE "demo_user"
      CLICK `#password`
      TYPE "demo_pass"
      CLICK `#login-btn`
      WAIT `.dashboard` 10
    ENDPROC

    # Execute login
    login

    # Verify success
    WAIT `.profile-section` 5
    """

    config = CrawlerRunConfig(actions=login_script, action_mode="crawl4ai_script")

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://example.com/login", config=config)

        print(f"Login success: {result.success}")
        return result


# ==============================================================================
# EXAMPLE 2: Form-Based Login (JavaScript)
# ==============================================================================


async def example_form_login_javascript():
    """Login using raw JavaScript"""

    js_script = """
    // Fill form fields
    document.getElementById('username').value = 'user@example.com';
    document.getElementById('password').value = 'password123';

    // Submit form
    document.querySelector('button[type="submit"]').click();

    // Wait for authentication
    await new Promise(resolve => {
        const checkAuth = setInterval(() => {
            if (document.querySelector('.authenticated-content')) {
                clearInterval(checkAuth);
                resolve();
            }
        }, 100);
        // Timeout after 10 seconds
        setTimeout(() => clearInterval(checkAuth), 10000);
    });
    """

    config = CrawlerRunConfig(actions=js_script, action_mode="javascript")

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://example.com/login", config=config)
        return result


# ==============================================================================
# EXAMPLE 3: Direct Cookie Injection
# ==============================================================================


async def example_cookie_injection():
    """Inject cookies directly into browser context"""

    browser_config = BrowserConfig(
        cookies=[
            {
                "name": "session_id",
                "value": "abc123xyz789",
                "domain": ".example.com",
                "path": "/",
                "httpOnly": True,
            },
            {
                "name": "preferences",
                "value": "dark_mode,notifications_on",
                "domain": ".example.com",
                "path": "/",
            },
        ]
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url="https://example.com/dashboard")
        print(f"Accessed with injected cookies: {result.success}")
        return result


# ==============================================================================
# EXAMPLE 4: Bearer Token Authentication
# ==============================================================================


async def example_bearer_token_auth():
    """Add Bearer token to request headers"""

    # Option A: Via BrowserConfig headers
    browser_config = BrowserConfig(
        headers={
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "X-API-Version": "2.0",
            "Accept": "application/json",
        }
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url="https://api.example.com/data")
        return result


# ==============================================================================
# EXAMPLE 5: Basic Authentication
# ==============================================================================


async def example_basic_auth():
    """Add Basic Authentication credentials"""

    async def auth_hook(page, context, url, **kwargs):
        """Inject Basic Auth header"""
        # Base64 encode credentials: username:password
        credentials = base64.b64encode(b"username:password").decode("ascii")

        await page.set_extra_http_headers({"Authorization": f"Basic {credentials}"})
        return page

    config = CrawlerRunConfig(hooks={"before_goto": auth_hook}, hooks_timeout=15)

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://example.com/protected", config=config)
        return result


# ==============================================================================
# EXAMPLE 6: Authentication via Hooks (Cookie-Based)
# ==============================================================================


async def example_auth_hooks_cookies():
    """Setup authentication using on_page_context_created hook"""

    async def auth_context_hook(page, context, **kwargs):
        """Add auth cookies and localStorage when context is created"""

        # Add authentication cookie
        await context.add_cookies(
            [
                {
                    "name": "auth_token",
                    "value": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "domain": ".example.com",
                    "path": "/",
                    "httpOnly": True,
                    "secure": True,
                }
            ]
        )

        # Set localStorage for additional auth data
        await page.evaluate("""
        localStorage.setItem('user_id', '12345');
        localStorage.setItem('auth_time', new Date().toISOString());
        localStorage.setItem('permissions', 'admin,editor');
        """)

        print("[HOOK] Authentication context initialized")
        return page

    config = CrawlerRunConfig(hooks={"on_page_context_created": auth_context_hook})

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://example.com/protected", config=config)
        return result


# ==============================================================================
# EXAMPLE 7: Authentication via Hooks (Header-Based)
# ==============================================================================


async def example_auth_hooks_headers():
    """Setup authentication using before_goto hook"""

    async def auth_headers_hook(page, context, url, **kwargs):
        """Add authentication headers before navigation"""

        await page.set_extra_http_headers(
            {
                "Authorization": "Bearer your_jwt_token_here",
                "X-API-Key": "your_api_key_here",
                "X-Request-ID": "unique_id_12345",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )

        print(f"[HOOK] Auth headers added for {url}")
        return page

    config = CrawlerRunConfig(
        hooks={"before_goto": auth_headers_hook}, hooks_timeout=15
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://api.example.com/data", config=config)
        return result


# ==============================================================================
# EXAMPLE 8: Persistent Session (Reusable Across Crawls)
# ==============================================================================


async def example_persistent_session():
    """Use persistent browser context to maintain session across multiple crawls"""

    # Create temp directory for browser profile
    profile_dir = tempfile.mkdtemp(prefix="crawl4ai_session_")

    try:
        browser_config = BrowserConfig(
            use_persistent_context=True,
            user_data_dir=profile_dir,
            headless=False,  # Set to True for production
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            print(f"[SESSION] Using profile: {profile_dir}")

            # CRAWL 1: Login and save session
            print("\n[CRAWL 1] Logging in...")
            login_config = CrawlerRunConfig(
                actions="""
                CLICK `#email`
                TYPE "user@example.com"
                CLICK `#password`
                TYPE "password123"
                CLICK `button[type="submit"]`
                WAIT `.authenticated-area` 10
                """
            )

            result1 = await crawler.arun(
                url="https://example.com/login", config=login_config
            )
            print(f"[CRAWL 1] Login success: {result1.success}")

            # Session is now saved in persistent profile

            # CRAWL 2: Access authenticated area (no re-login)
            print("\n[CRAWL 2] Accessing dashboard...")
            result2 = await crawler.arun(
                url="https://example.com/dashboard"
                # No login config needed - session already authenticated
            )
            print(f"[CRAWL 2] Dashboard access success: {result2.success}")

            # CRAWL 3: Another authenticated area
            print("\n[CRAWL 3] Accessing profile...")
            result3 = await crawler.arun(url="https://example.com/profile")
            print(f"[CRAWL 3] Profile access success: {result3.success}")

            return result1, result2, result3

    finally:
        # Cleanup profile directory
        import shutil

        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir)
            print(f"\n[SESSION] Cleaned up profile: {profile_dir}")


# ==============================================================================
# EXAMPLE 9: OAuth Authentication Flow
# ==============================================================================


async def example_oauth_flow():
    """Handle OAuth/SSO authentication with multiple steps"""

    oauth_script = """
    # Step 1: Click login with OAuth provider
    CLICK `a.login-with-google`
    WAIT `input#email` 5

    # Step 2: Enter email
    CLICK `input#email`
    TYPE "user@gmail.com"
    CLICK `button#next`
    WAIT `input#password` 5

    # Step 3: Enter password
    CLICK `input#password`
    TYPE "password123"
    CLICK `button#signin`
    WAIT `.permissions-screen` 5

    # Step 4: Approve permissions
    IF EXISTS `button#approve` THEN
      CLICK `button#approve`
    ENDIF
    WAIT `.dashboard` 10
    """

    config = CrawlerRunConfig(actions=oauth_script, action_mode="crawl4ai_script")

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://example.com/login", config=config)
        return result


# ==============================================================================
# EXAMPLE 10: Multi-Factor Authentication (MFA/2FA)
# ==============================================================================


async def example_mfa_authentication():
    """Handle multi-factor authentication (email/SMS code)"""

    # Note: In production, you'd retrieve the code from email/SMS
    mfa_code = "123456"  # Example code

    mfa_script = f"""
    # Step 1: Initial login
    CLICK `#username`
    TYPE "user@example.com"
    CLICK `#password`
    TYPE "password123"
    CLICK `#login-btn`
    WAIT `.mfa-prompt` 10

    # Step 2: MFA code entry
    CLICK `#mfa-code-input`
    TYPE "{mfa_code}"
    CLICK `#verify-mfa`
    WAIT `.dashboard` 10
    """

    config = CrawlerRunConfig(actions=mfa_script, action_mode="crawl4ai_script")

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://example.com/login", config=config)
        return result


# ==============================================================================
# EXAMPLE 11: Combined Cookie + Header Authentication
# ==============================================================================


async def example_combined_auth():
    """Use both cookies and custom headers for maximum compatibility"""

    browser_config = BrowserConfig(
        cookies=[
            {
                "name": "session_id",
                "value": "sess_abc123xyz",
                "domain": ".api.example.com",
                "path": "/",
            }
        ],
        headers={
            "Authorization": "Bearer jwt_token_here",
            "X-API-Key": "api_key_12345",
            "X-Client-Version": "2.0",
            "Accept": "application/json",
        },
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url="https://api.example.com/protected")
        return result


# ==============================================================================
# EXAMPLE 12: Docker Client with Bearer Token
# ==============================================================================


async def example_docker_client_auth():
    """Use Crawl4AI Docker client with Bearer token authentication"""

    import aiohttp

    api_token = "your_api_token_here"
    headers = {"Authorization": f"Bearer {api_token}"}

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "http://localhost:8000/crawl/https://example.com", headers=headers
        ) as response:
            result = await response.json()
            print(f"Docker client result: {result}")
            return result


# ==============================================================================
# EXAMPLE 13: Export/Import Storage State
# ==============================================================================


async def example_storage_state_management():
    """Export browser storage state (cookies + localStorage) for backup"""

    storage_file = "/tmp/auth_storage_state.json"

    # STEP 1: Login and export storage state
    browser_config = BrowserConfig(
        use_persistent_context=True, user_data_dir=tempfile.mkdtemp()
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Login and save session
        config = CrawlerRunConfig(
            actions="""
            CLICK `#username`
            TYPE "user@example.com"
            CLICK `#password`
            TYPE "password"
            CLICK `button[type="submit"]`
            WAIT `.authenticated` 10
            """
        )

        result = await crawler.arun(url="https://example.com/login", config=config)

        # Export storage state for later use
        # In production, you'd save this to a file
        print(f"Storage state exported to: {storage_file}")

    # STEP 2: Load storage state in new browser session
    browser_config_restored = BrowserConfig(
        storage_state=storage_file  # Load from file
    )

    async with AsyncWebCrawler(config=browser_config_restored) as crawler:
        # No login needed - state restored
        result = await crawler.arun(url="https://example.com/dashboard")
        print(f"Accessed authenticated area with restored state: {result.success}")


# ==============================================================================
# EXAMPLE 14: Retry Logic for Failed Authentication
# ==============================================================================


async def example_auth_with_retry():
    """Implement retry logic for authentication failures"""

    max_retries = 3
    retry_count = 0

    browser_config = BrowserConfig(
        use_persistent_context=True, user_data_dir=tempfile.mkdtemp()
    )

    while retry_count < max_retries:
        try:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                config = CrawlerRunConfig(
                    actions="""
                    CLICK `#username`
                    TYPE "user@example.com"
                    CLICK `#password`
                    TYPE "password"
                    CLICK `#login-btn`
                    WAIT `.dashboard` 10
                    """
                )

                result = await crawler.arun(
                    url="https://example.com/login", config=config
                )

                # Check if authentication succeeded
                if result.success and ".dashboard" in result.html:
                    print(f"[AUTH] Success on attempt {retry_count + 1}")
                    return result
                else:
                    raise Exception("Authentication check failed")

        except Exception as e:
            retry_count += 1
            print(f"[AUTH] Attempt {retry_count} failed: {e}")

            if retry_count >= max_retries:
                print(f"[AUTH] Failed after {max_retries} attempts")
                raise

            # Wait before retry
            await asyncio.sleep(2**retry_count)  # Exponential backoff


# ==============================================================================
# EXAMPLE 15: Monitor Authentication via Hooks
# ==============================================================================


async def example_auth_monitoring():
    """Monitor and log authentication events using hooks"""

    async def monitor_auth_hook(page, context, **kwargs):
        """Monitor authentication-related events"""

        # Check for auth cookies
        cookies = await context.cookies()
        auth_cookies = [c for c in cookies if "auth" in c["name"].lower()]

        print(f"[MONITOR] Found {len(auth_cookies)} auth cookies:")
        for cookie in auth_cookies:
            print(f"  - {cookie['name']}: {cookie['value'][:20]}...")

        # Check for auth headers
        storage = await page.evaluate("""
        (() => {
            return {
                user_id: localStorage.getItem('user_id'),
                auth_time: localStorage.getItem('auth_time'),
                permissions: localStorage.getItem('permissions')
            }
        })()
        """)

        print("[MONITOR] Auth state in localStorage:")
        print(f"  - User ID: {storage.get('user_id')}")
        print(f"  - Auth Time: {storage.get('auth_time')}")
        print(f"  - Permissions: {storage.get('permissions')}")

        return page

    config = CrawlerRunConfig(hooks={"on_page_context_created": monitor_auth_hook})

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://example.com/protected", config=config)
        return result


# ==============================================================================
# MAIN: Run examples
# ==============================================================================

if __name__ == "__main__":
    print("Crawl4AI Authentication Examples")
    print("=" * 60)

    # You can uncomment and run individual examples:
    # asyncio.run(example_form_login_c4a_script())
    # asyncio.run(example_cookie_injection())
    # asyncio.run(example_bearer_token_auth())
    # asyncio.run(example_persistent_session())
    # etc.

    print("\nTo run examples, uncomment them in the __main__ block")
    print("Each example is independent and can be called individually")
