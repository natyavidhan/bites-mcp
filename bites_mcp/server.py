"""MCP server exposing a Bites deployment's site-publishing API as tools.

Configured entirely through environment variables:
  BITES_URL      the URL where the Bites app is deployed (e.g. a Vercel URL)
  BITES_API_KEY  the API_KEY configured on that deployment

Run with `bites-mcp` (after install) or `python -m bites_mcp.server`.
"""
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from bites_mcp.client import BitesClient, BitesError

load_dotenv()  # no-op if there's no .env; lets local testing use one

mcp = FastMCP(
    name="bites",
    instructions=(
        "Tools for publishing and managing single-file HTML or Markdown pages "
        "on a Bites deployment. Call check_connection first if you're not sure "
        "the configured BITES_URL/BITES_API_KEY work. Use create_site to "
        "publish new content and get back its live URL, list_sites/get_site to "
        "see what's already published, update_site to edit, re-theme, rename, "
        "or (un)publish an existing page, and delete_site to remove one."
    ),
)


def _client() -> BitesClient:
    try:
        return BitesClient()
    except BitesError as e:
        raise RuntimeError(str(e)) from e


@mcp.tool()
def check_connection() -> dict:
    """Verify the configured Bites URL and API key are reachable and valid."""
    return _client().ping()


@mcp.tool()
def list_themes() -> dict:
    """List the Markdown rendering themes available on this Bites deployment.

    Returns {"themes": [...]}. Each entry has a `slug` (pass this as
    create_site's/update_site's markdown_theme), a display `name`, and a
    `family` ("classic" for the GitHub Pages themes or "modern" for
    color-scheme themes like Dracula/Nord).
    """
    return {"themes": _client().list_themes()}


@mcp.tool()
def list_sites() -> dict:
    """List every site currently hosted on this Bites deployment, newest first.

    Returns {"sites": [...]}.
    """
    return {"sites": _client().list_sites()}


@mcp.tool()
def get_site(slug_or_id: str) -> dict:
    """Get a site's full details, including its raw HTML/Markdown source.

    Args:
        slug_or_id: The site's URL slug (the part after the domain) or its
            database id, as returned by list_sites/create_site.
    """
    return _client().get_site(slug_or_id)


@mcp.tool()
def create_site(
    content: str,
    source_type: str,
    title: Optional[str] = None,
    slug: Optional[str] = None,
    markdown_theme: Optional[str] = None,
    is_public: Optional[bool] = None,
    protected: Optional[bool] = None,
    protect_username: Optional[str] = None,
    protect_password: Optional[str] = None,
) -> dict:
    """Publish a new single-file site and return it, including its live URL.

    Args:
        content: The full page to publish: a complete HTML document (CSS/JS
            inline is fine) or Markdown source.
        source_type: "html" to serve content as-is, or "markdown" to render
            it server-side with the chosen markdown_theme.
        title: Page title. Defaults to the slug if omitted.
        slug: URL path segment; the page is published at
            <bites-url>/<slug>. Auto-generated from the title (or content)
            if omitted — call list_sites first if you need a specific,
            guaranteed-available name.
        markdown_theme: Only used when source_type is "markdown". A slug from
            list_themes, e.g. "github-light" (default), "dracula", "cayman".
        is_public: Whether the page is publicly reachable. Defaults to true;
            set false to keep it unpublished (admin-only preview) for now.
        protected: If true, visitors must authenticate with
            protect_username/protect_password (HTTP Basic Auth) to view it.
        protect_username: Required if protected is true.
        protect_password: Required if protected is true.
    """
    return _client().create_site(
        content=content,
        source_type=source_type,
        title=title,
        slug=slug,
        markdown_theme=markdown_theme,
        is_public=is_public,
        protected=protected,
        protect_username=protect_username,
        protect_password=protect_password,
    )


@mcp.tool()
def update_site(
    slug_or_id: str,
    content: Optional[str] = None,
    source_type: Optional[str] = None,
    title: Optional[str] = None,
    slug: Optional[str] = None,
    markdown_theme: Optional[str] = None,
    is_public: Optional[bool] = None,
    protected: Optional[bool] = None,
    protect_username: Optional[str] = None,
    protect_password: Optional[str] = None,
) -> dict:
    """Update an existing site. Only the arguments you pass are changed.

    Args:
        slug_or_id: The site to update, by its current slug or database id.
        content: New page content, replacing the current body. Pass
            source_type too if the content type is changing.
        source_type: "html" or "markdown", if changing content's type.
        title: New title.
        slug: New URL slug, to rename/move the page.
        markdown_theme: New theme slug (see list_themes); only applies while
            the site's source_type is "markdown".
        is_public: Set false to unpublish, true to (re)publish.
        protected: Enable/disable the per-site HTTP Basic Auth requirement.
        protect_username: New protected-site username.
        protect_password: New protected-site password. If protected stays
            true and this is omitted, the existing password is kept.
    """
    return _client().update_site(
        slug_or_id,
        content=content,
        source_type=source_type,
        title=title,
        slug=slug,
        markdown_theme=markdown_theme,
        is_public=is_public,
        protected=protected,
        protect_username=protect_username,
        protect_password=protect_password,
    )


@mcp.tool()
def delete_site(slug_or_id: str) -> dict:
    """Permanently delete a site from Bites, by its slug or database id."""
    return _client().delete_site(slug_or_id)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
