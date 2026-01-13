# Crawl4AI Authentication & Login Capabilities Research

## Executive Summary

Crawl4AI **fully supports authenticated crawling** with comprehensive capabilities for session management, cookie handling, and login automation. The library provides multiple authentication patterns suitable for different authentication schemes (form-based, token-based, OAuth, Basic Auth).

---

## 1. Session Management & Cookie Handling

### Persistent Context
Crawl4AI supports persistent browser contexts that maintain cookies, localStorage, and sessionStorage across crawls:

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig

browser_config = BrowserConfig(
    use_persistent_context=True,
    user_data_dir="/path/to/profile",  # Optional: specify profile directory
)

async with AsyncWebCrawler(config=browser_config) as crawler:
    result = await crawler.arun(url="https://example.com")
```

**Key Parameters:**
- `use_persistent_context: bool` - Enable persistent browser profile (automatically sets `use_managed_browser=True`)
- `user_data_dir: str` - Path to user data directory for persistent sessions. If None, a temporary directory is used.

### Cookie Management

#### Adding Cookies Programmatically
```python
browser_config = BrowserConfig(
    cookies=[
        {"name": "session_id", "value": "abc123", "url": "https://example.com"},
        {"name": "preferences", "value": "dark_mode", "url": "https://example.com"},
        {
            "name": "auth_token",
            "value": "jwt_token_here",
            "domain": ".example.com",
            "path": "/",
            "httpOnly": True,
            "secure": True
        }
    ]
)
```

#### Loading Cookies from Captcha Solvers
Cookies from external solvers (like CapSolver) can be directly injected:

```python
# Example: Using cookies from CapSolver Cloudflare challenge solution
cookies_from_solver = solution["cookies"]  # From CapSolver API
user_agent = solution["userAgent"]

cookies_list = []
for name, value in cookies_from_solver.items():
    cookies_list.append({
        "name": name,
        "value": value,
        "url": site_url,
    })

browser_config = BrowserConfig(
    use_persistent_context=True,
    user_agent=user_agent,
    cookies=cookies_list,
)
```

### Storage State Management

Crawl4AI can import/export complete browser state (cookies + localStorage):

```python
# Export storage state (cookies, localStorage, sessionStorage)
storage_state = await context.storage_state(path="/path/to/storage_state.json")

# Import storage state in future crawls
browser_config = BrowserConfig(
    storage_state=storage_state  # Can be dict or path string
)
```

---

## 2. Form-Based Login Automation

### Using C4A Script (High-Level, Recommended)

Crawl4AI provides `crawl4ai_script` (C4A), a declarative scripting language for browser automation:

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

login_script = """
# Define reusable login procedure
PROC login
  CLICK `#username`
  TYPE "your_username"
  CLICK `#password`
  TYPE "your_password"
  CLICK `#login-btn`
  WAIT `.dashboard` 10  # Wait for dashboard element, timeout 10s
ENDPROC

# Main workflow
login
WAIT `#content-area` 5
"""

config = CrawlerRunConfig(
    actions=login_script,
    action_mode="crawl4ai_script"
)

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(
        url="https://example.com/login",
        config=config
    )
```

**C4A Commands for Authentication:**
- `CLICK selector` - Click form elements
- `TYPE text` - Type text into focused field
- `SET selector value` - Set field value directly
- `WAIT selector timeout` - Wait for element appearance
- `PROC name ... ENDPROC` - Define reusable procedures
- `IF/ELSE/ENDIF` - Conditional logic

### Using JavaScript

For complex scenarios requiring direct DOM manipulation:

```python
config = CrawlerRunConfig(
    actions="""
    // Fill and submit login form
    document.getElementById('username').value = 'your_username';
    document.getElementById('password').value = 'your_password';
    document.querySelector('button[type="submit"]').click();

    // Wait for redirect
    await new Promise(r => setTimeout(r, 2000));
    """,
    action_mode="javascript"
)
```

---

## 3. Hook-Based Authentication

### Authentication Hooks System

Crawl4AI provides hooks that execute at different lifecycle stages. Common authentication hooks:

#### Hook 1: `on_page_context_created` - Add Cookies/LocalStorage
Executes when a new browser context is created (before any navigation):

```python
async def auth_context_hook(page, context, **kwargs):
    """Setup authentication context"""
    print("[HOOK] Setting up authentication")

    # Add authentication cookies
    await context.add_cookies([{
        "name": "auth_token",
        "value": "fake_jwt_token",
        "domain": ".example.com",
        "path": "/",
        "httpOnly": True
    }])

    # Set localStorage values
    await page.evaluate('''
    localStorage.setItem('user_id', '12345');
    localStorage.setItem('auth_time', new Date().toISOString());
    ''')

    print("[HOOK] Auth context ready")
    return page
```

#### Hook 2: `before_goto` - Add HTTP Headers
Executes before navigation, allowing header injection:

```python
import base64

async def auth_headers_hook(page, context, url, **kwargs):
    """Add authentication headers before navigation"""
    print(f"[HOOK] Adding auth headers for {url}")

    # Basic Authentication
    credentials = base64.b64encode(b"username:password").decode('ascii')

    # Bearer Token
    auth_token = "your_jwt_token_here"

    await page.set_extra_http_headers({
        'Authorization': f'Basic {credentials}',
        # OR: 'Authorization': f'Bearer {auth_token}',
        'X-API-Key': 'test-key-123',
        'Accept-Language': 'en-US'
    })

    return page
```

#### Hook 3: `on_user_agent_updated` - Setup After UA Change
Executes after user agent is updated (good timing for auth setup):

```python
async def setup_auth_after_ua(page, context, **kwargs):
    """Setup auth after user agent changes"""
    await context.add_cookies([...])
    return page
```

### Using Hooks in Crawl Config

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

config = CrawlerRunConfig(
    hooks={
        "on_page_context_created": auth_context_hook,
        "before_goto": auth_headers_hook
    },
    hooks_timeout=15  # Timeout for hook execution
)

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(
        url="https://httpbin.org/basic-auth/user/passwd",
        config=config
    )
```

---

## 4. Token-Based Authentication (API)

### Bearer Token Authentication

For REST API endpoints secured with Bearer tokens:

```python
import aiohttp
import json

async def api_example():
    """Example of using crawl4ai API with Bearer token"""
    api_token = "your_api_token_here"
    headers = {"Authorization": f"Bearer {api_token}"}

    async with aiohttp.ClientSession() as session:
        # Submit crawl job
        crawl_request = {
            "urls": ["https://example.com"],
            "extraction_config": {
                "type": "schema",
                "schema": {"name": "string", "price": "number"}
            }
        }

        async with session.post(
            "http://localhost:8000/crawl",
            json=crawl_request,
            headers=headers
        ) as response:
            result = await response.json()
            print(result)
```

### Docker Client with Token Auth

```python
from crawl4ai.docker_client import Crawl4aiDockerClient

api_token = "your_api_token"
headers = {"Authorization": f"Bearer {api_token}"}

async with aiohttp.ClientSession() as session:
    async with session.get(
        "http://localhost:8000/crawl/https://example.com",
        headers=headers
    ) as response:
        result = await response.json()
```

---

## 5. OAuth & SSO Authentication

### Generic OAuth Flow Pattern

For OAuth-protected sites, use the full flow:

```python
oauth_script = """
# Step 1: Click login button
CLICK `#login-with-oauth`
WAIT `.oauth-modal` 5

# Step 2: Enter credentials (on OAuth provider)
CLICK `#email`
TYPE "user@example.com"
CLICK `#next`
WAIT `#password` 5

CLICK `#password`
TYPE "password123"
CLICK `#signin`

# Step 3: Approve permissions
WAIT `#approve-btn` 5
CLICK `#approve-btn`

# Step 4: Wait for redirect back
WAIT `.dashboard` 10
"""

config = CrawlerRunConfig(
    actions=oauth_script,
    action_mode="crawl4ai_script"
)

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(
        url="https://example.com/login",
        config=config
    )
```

---

## 6. Advanced Patterns

### Session Reuse Across Multiple Crawls

```python
import tempfile
import os

async def authenticated_crawling_session():
    """Maintain authenticated session across multiple crawls"""

    # Create temporary user data directory
    temp_dir = tempfile.mkdtemp()

    try:
        browser_config = BrowserConfig(
            use_persistent_context=True,
            user_data_dir=temp_dir,
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            # First crawl: Login
            login_config = CrawlerRunConfig(
                actions="""
                CLICK `#username`
                TYPE "user@example.com"
                CLICK `#password`
                TYPE "password"
                CLICK `#login`
                WAIT `.authenticated-content` 10
                """
            )

            result1 = await crawler.arun(
                url="https://example.com/login",
                config=login_config
            )

            # Session is now persisted in browser profile

            # Second crawl: Access authenticated area (no re-login needed)
            result2 = await crawler.arun(
                url="https://example.com/dashboard",
                # Session cookies still present from first crawl
            )

            # Third crawl: Different authenticated area
            result3 = await crawler.arun(
                url="https://example.com/profile"
            )

            return result1, result2, result3
    finally:
        # Cleanup
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
```

### Cookie + Header Combination

```python
browser_config = BrowserConfig(
    cookies=[
        {"name": "session", "value": "abc123", "url": "https://api.example.com"}
    ],
    headers={
        "Authorization": "Bearer jwt_token_here",
        "X-API-Version": "2.0"
    }
)
```

### Handling Multi-Step Authentication

```python
multistep_auth = """
# Step 1: Initial login form
CLICK `#username`
TYPE "user@example.com"
CLICK `#password`
TYPE "password"
CLICK `#login`
WAIT `#mfa-prompt` 10

# Step 2: MFA/2FA
CLICK `#mfa-code`
TYPE "123456"
CLICK `#verify`
WAIT `.dashboard` 10

# Step 3: Verify we're authenticated
IF EXISTS `.protected-content` THEN
  CLICK `.menu`
  WAIT `.profile` 3
ENDIF
"""

config = CrawlerRunConfig(
    actions=multistep_auth,
    action_mode="crawl4ai_script"
)
```

---

## 7. Real-World Examples from Repository

### Example 1: Basic Authentication with Hooks

```python
# From: docs/examples/docker_client_hooks_example.py

async def auth_context_hook(page, context, **kwargs):
    await context.add_cookies([{
        "name": "auth_token",
        "value": "fake_jwt_token",
        "domain": ".httpbin.org",
        "path": "/",
        "httpOnly": True
    }])
    await page.evaluate('''
    localStorage.setItem('user_id', '12345');
    localStorage.setItem('auth_time', new Date().toISOString());
    ''')
    return page

async def test_authentication():
    async with Crawl4aiDockerClient(base_url="http://localhost:8000") as client:
        hooks = {
            "on_page_context_created": auth_context_hook,
        }
        result = await client.crawl(
            ["https://httpbin.org/cookies"],
            hooks=hooks,
            hooks_timeout=15
        )
```

### Example 2: Cookie Injection from CapSolver

```python
# From: docs/examples/capsolver_captcha_solver/capsolver_api_integration/solve_cloudflare_challenge.py

from crawl4ai import AsyncWebCrawler, BrowserConfig

# Get cookies from CapSolver after solving challenge
cookies = solution["cookies"]
user_agent = solution["userAgent"]

cookies_list = [
    {"name": name, "value": value, "url": site_url}
    for name, value in cookies.items()
]

browser_config = BrowserConfig(
    verbose=True,
    headless=False,
    use_persistent_context=True,
    user_agent=user_agent,
    cookies=cookies_list,
)

async with AsyncWebCrawler(config=browser_config) as crawler:
    result = await crawler.arun(url=site_url)
```

### Example 3: C4A Script Login

```python
# From: docs/examples/c4a_script/demo_c4a_crawl4ai.py

workflow_script = """
PROC login
  CLICK `#username`
  TYPE "demo_user"
  CLICK `#password`
  TYPE "demo_pass"
  CLICK `#login-btn`
  WAIT `.dashboard` 10
ENDPROC

login
CLICK `.profile-link`
WAIT `.user-info` 5
"""
```

---

## 8. BrowserConfig Authentication Parameters

Complete documentation of authentication-related BrowserConfig parameters:

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `cookies` | `list[dict]` | `[]` | List of cookies to inject, each with name/value/url/domain/path |
| `headers` | `dict` | `{}` | Extra HTTP headers applied to all requests in context |
| `storage_state` | `str\|dict\|None` | `None` | Complete storage state (cookies + localStorage + sessionStorage) |
| `use_persistent_context` | `bool` | `False` | Enable persistent browser profile across sessions |
| `user_data_dir` | `str\|None` | `None` | Path to persistent profile directory |
| `ignore_https_errors` | `bool` | `True` | Bypass HTTPS certificate validation (useful for some auth redirects) |

---

## 9. Key Findings Summary

### Supported Authentication Methods
✅ **Form-based Login** - Full automation via C4A Script or JavaScript
✅ **Cookie Injection** - Direct cookie management with flexible properties
✅ **Bearer Tokens** - HTTP header injection with Authorization headers
✅ **Basic Auth** - Base64-encoded credentials in headers
✅ **Custom Headers** - Arbitrary header injection for API keys, versioning, etc.
✅ **Persistent Sessions** - Browser profile persistence with user_data_dir
✅ **OAuth/SSO** - Multi-step automation with wait conditions
✅ **MFA/2FA** - Step-by-step automation with conditional logic
✅ **Storage State** - Import/export complete browser state

### Hook Lifecycle for Authentication
1. `on_driver_created` - Early hook (legacy)
2. `on_page_context_created` - Add cookies/localStorage (RECOMMENDED)
3. `before_goto` - Inject headers before first navigation
4. `on_user_agent_updated` - Post-UA-change setup
5. `on_response` - Monitor/modify responses
6. `on_request` - Intercept/modify requests

### Best Practices
1. **Use persistent context** when reusing sessions across multiple crawls
2. **Add cookies via hooks** for better lifecycle control
3. **Inject headers in `before_goto`** hook before navigation
4. **Use C4A Script** for readable, maintainable login automation
5. **Combine cookies + headers** for maximum compatibility
6. **Store/export storage state** for backup and portability
7. **Use timeouts** in WAIT commands to prevent indefinite hangs

---

## 10. Integration Checklist

- [ ] Determine authentication method (form, token, OAuth, etc.)
- [ ] Create browser config with appropriate parameters (cookies, headers, persistence)
- [ ] Implement authentication hooks if needed
- [ ] Define login automation script (C4A or JavaScript)
- [ ] Test with single URL to verify auth works
- [ ] Set up session reuse across multiple crawls
- [ ] Configure fallback/retry logic for failed auth
- [ ] Monitor/log authentication events via hooks
- [ ] Export storage state for backup/portability
- [ ] Document credentials management (env vars, secure storage)

---

## 11. Limitations & Considerations

1. **Headless Mode** - Some complex OAuth flows may require headless=False
2. **Cloudflare/WAF** - May need additional solving via CapSolver integration
3. **Fingerprinting** - Some sites detect browser automation; consider user_agent_mode="random"
4. **Session Timeouts** - Persistent sessions may expire; implement refresh logic
5. **Cookie Scope** - Cookies must match domain; use proper domain/path properties

---

## References

**Repository:** https://github.com/unclecode/crawl4ai
**Documentation:** Check docs/examples/ for more authentication patterns
**Key Files:**
- `crawl4ai/async_configs.py` - BrowserConfig definitions
- `crawl4ai/browser_manager.py` - Cookie/storage management
- `docs/examples/docker_client_hooks_example.py` - Hook examples
- `docs/examples/c4a_script/demo_c4a_crawl4ai.py` - C4A Script examples
- `crawl4ai/prompts.py` - GENERATE_SCRIPT_PROMPT with usage guidelines
