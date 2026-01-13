# Crawl4AI Authentication - Quick Reference Guide

## 5-Minute Quick Start

### Scenario 1: Form-Based Login (Most Common)

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

login_script = """
CLICK `#username`
TYPE "user@example.com"
CLICK `#password`
TYPE "password123"
CLICK `button[type="submit"]`
WAIT `.dashboard` 10
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

### Scenario 2: Direct Cookie Injection

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig

config = BrowserConfig(
    cookies=[
        {
            "name": "session_id",
            "value": "abc123xyz",
            "domain": ".example.com",
            "path": "/"
        }
    ]
)

async with AsyncWebCrawler(config=config) as crawler:
    result = await crawler.arun(url="https://example.com/profile")
```

### Scenario 3: Bearer Token (API)

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig

config = BrowserConfig(
    headers={
        "Authorization": "Bearer your_jwt_token_here",
        "X-API-Key": "optional_api_key"
    }
)

async with AsyncWebCrawler(config=config) as crawler:
    result = await crawler.arun(url="https://api.example.com/data")
```

### Scenario 4: Persistent Session (Reusable)

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig

config = BrowserConfig(
    use_persistent_context=True,
    user_data_dir="/path/to/profile"
)

async with AsyncWebCrawler(config=config) as crawler:
    # First crawl: Login and session is saved
    await crawler.arun(
        url="https://example.com/login",
        config=CrawlerRunConfig(
            actions="""
            CLICK `#username`
            TYPE "user@example.com"
            CLICK `#password`
            TYPE "password"
            CLICK `button[type="submit"]`
            WAIT `.dashboard` 10
            """
        )
    )

    # Second crawl: Session reused, no re-login needed
    result = await crawler.arun(url="https://example.com/dashboard")
```

### Scenario 5: Authentication Hooks

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def setup_auth(page, context, **kwargs):
    await context.add_cookies([{
        "name": "auth_token",
        "value": "jwt_token_here",
        "domain": ".example.com"
    }])
    return page

config = CrawlerRunConfig(
    hooks={"on_page_context_created": setup_auth}
)

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(
        url="https://example.com",
        config=config
    )
```

---

## C4A Script Commands Reference

| Command | Syntax | Example | Purpose |
|---------|--------|---------|---------|
| **CLICK** | `CLICK selector` | `CLICK #submit-btn` | Click element |
| **TYPE** | `TYPE text` | `TYPE "password123"` | Type into focused field |
| **SET** | `SET selector value` | `SET #email user@test.com` | Set field value directly |
| **WAIT** | `WAIT selector timeout` | `WAIT .dashboard 10` | Wait for element (seconds) |
| **SCROLL** | `SCROLL down/up distance` | `SCROLL down 500` | Scroll page |
| **IF/ENDIF** | `IF EXISTS selector THEN ... ENDIF` | Check element existence | Conditional logic |
| **PROC/ENDPROC** | `PROC name ... ENDPROC` | Reusable procedures | Define reusable blocks |

---

## Authentication Methods Comparison

| Method | Setup Time | Persistence | Complexity | Best For |
|--------|-----------|-------------|-----------|----------|
| **Form Login** | Medium | Good (with persistent context) | Medium | User-based access |
| **Cookie Injection** | Low | Per-crawl | Low | Simple session-based auth |
| **Bearer Token** | Low | Per-crawl | Low | API authentication |
| **Hooks** | Medium | Per-crawl (customizable) | High | Complex auth flows |
| **Persistent Context** | High (setup) | Excellent (saved profile) | Low | Multi-session reuse |

---

## Cookie Format Reference

```python
{
    "name": "session_id",           # Required: cookie name
    "value": "abc123",              # Required: cookie value
    "url": "https://example.com",   # Optional: URL scope
    "domain": ".example.com",       # Optional: domain scope
    "path": "/",                    # Optional: path scope
    "httpOnly": True,               # Optional: HTTP-only flag
    "secure": True,                 # Optional: HTTPS-only flag
    "sameSite": "Lax",              # Optional: SameSite policy
    "expires": 1704067200           # Optional: expiration timestamp
}
```

---

## Common Authentication Patterns

### Pattern 1: Username/Password Form
```python
script = """
CLICK `input[name="username"]`
TYPE "user@example.com"
CLICK `input[name="password"]`
TYPE "mypassword"
CLICK `button[type="submit"]`
WAIT `.authenticated-area` 10
"""
```

### Pattern 2: OAuth Approval Flow
```python
script = """
CLICK `a.google-login`
WAIT `input[name="email"]` 5
TYPE "user@gmail.com"
CLICK `button#next`
WAIT `input[name="password"]` 5
TYPE "password"
CLICK `button#submit`
WAIT `.approval-screen` 5
CLICK `button#approve`
WAIT `.dashboard` 10
"""
```

### Pattern 3: MFA/2FA
```python
script = """
CLICK `#username`
TYPE "user@example.com"
CLICK `#password`
TYPE "password"
CLICK `#login-btn`
WAIT `.mfa-prompt` 10
CLICK `#mfa-code`
TYPE "123456"
CLICK `#verify-mfa`
WAIT `.dashboard` 10
"""
```

### Pattern 4: Check & Wait for Auth
```python
script = """
# Try to access protected page
GOTO https://example.com/dashboard
WAIT 2

# Check if authenticated, if not, login
IF NOT EXISTS `.authenticated-badge` THEN
  CLICK `#login-btn`
  WAIT `#username` 5
  CLICK `#username`
  TYPE "user@example.com"
  CLICK `#password`
  TYPE "password"
  CLICK `button[type="submit"]`
  WAIT `.dashboard` 10
ENDIF
"""
```

---

## Troubleshooting

### Problem: Auth keeps failing
**Solutions:**
- Increase WAIT timeout values
- Check CSS selectors are correct
- Verify credentials in credentials
- Add verbose logging to see what's happening
- Use headless=False to debug interactively

### Problem: Session not persisting
**Solutions:**
- Ensure use_persistent_context=True
- Set valid user_data_dir path
- Verify cookies have correct domain/path
- Check browser isn't clearing cookies

### Problem: Headers not being sent
**Solutions:**
- Headers must be set before navigation (use before_goto hook)
- Verify header format: "Authorization": "Bearer token"
- Some sites ignore custom headers

### Problem: "Detected automation"
**Solutions:**
- Use random user agents: user_agent_mode="random"
- Add delays between actions
- Use headless=False for visual crawling
- Inject navigator override scripts

---

## Environment Variables Pattern

```python
import os
from crawl4ai import AsyncWebCrawler, BrowserConfig

# Load from environment
username = os.getenv("CRAWL_USERNAME")
password = os.getenv("CRAWL_PASSWORD")
api_token = os.getenv("CRAWL_API_TOKEN")

# Use in config
config = BrowserConfig(
    headers={
        "Authorization": f"Bearer {api_token}"
    }
)

# Use in script
script = f"""
CLICK `#username`
TYPE "{username}"
CLICK `#password`
TYPE "{password}"
CLICK `button[type="submit"]`
WAIT `.dashboard` 10
"""
```

---

## Complete Example: LinkedIn-Style Login

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig

async def login_to_site():
    # Login script
    login_script = """
    # Navigate to login if needed
    CLICK `a[href="/login"]`
    WAIT `#username` 5

    # Fill username
    CLICK `#username`
    TYPE "your_email@example.com"

    # Fill password
    CLICK `#password`
    TYPE "your_password"

    # Submit
    CLICK `button[type="submit"]`
    WAIT `.feed` 10

    # Verify login success
    IF EXISTS `.profile-badge` THEN
      CLICK `.settings`
      WAIT `.settings-menu` 3
    ENDIF
    """

    # Browser config with persistence
    browser_config = BrowserConfig(
        use_persistent_context=True,
        user_data_dir="./session_data",
        headless=False,  # See login happen
    )

    # Crawl config with script
    crawl_config = CrawlerRunConfig(
        actions=login_script,
        action_mode="crawl4ai_script"
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://example.com",
            config=crawl_config
        )

        print(f"Success: {result.success}")
        print(f"Authenticated: {'.profile-badge' in result.html}")

        return result

# Run
asyncio.run(login_to_site())
```

---

## Key Takeaways

1. **Choose the right method**: Form script for complexity, cookies for simplicity
2. **Use persistent context**: Saves login state across multiple crawls
3. **Combine strategies**: Use cookies + headers together for reliability
4. **Test incrementally**: Start with single crawl before multi-session automation
5. **Store credentials safely**: Use environment variables, never hardcode
6. **Monitor success**: Check for authenticated elements in results
7. **Handle failures gracefully**: Implement retry logic with wait conditions

---

## Resources

- **Full Research:** `crawl4ai_authentication_research.md`
- **Repository:** https://github.com/unclecode/crawl4ai
- **C4A Script Guide:** `crawl4ai/prompts.py` (GENERATE_SCRIPT_PROMPT)
