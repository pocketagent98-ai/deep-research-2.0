import logging
import time

logger = logging.getLogger(__name__)

# Response codes worth one retry: rate limiting and transient server errors.
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_CONTENT_BYTES = 10 * 1024 * 1024  # Skip pages larger than 10MB


class TrafilaturaScraper:
    """Clean-text web scraper powered by Trafilatura.

    Trafilatura removes ads, navigation, boilerplate and layout, and extracts
    only the main article text — usually noticeably cleaner than generic
    BeautifulSoup heuristics, which improves research quality and saves tokens.

    Requires:  pip install trafilatura
    Enable:    set SCRAPER=trafilatura in .env
    """

    def __init__(self, link, session=None):
        self.link = link
        self.session = session

    def scrape(self):
        """Fetch the page and extract clean main-content text, images and title.

        Returns:
            Tuple of (content, image_urls, title). Empty values are returned
            when the page cannot be fetched or yields no usable content.
        """
        try:
            import trafilatura
        except ImportError:
            logger.error(
                "trafilatura is not installed. Run: pip install trafilatura "
                "(or see requirements-free.txt)"
            )
            return "", [], ""

        response = self._fetch()
        if response is None:
            return "", [], ""

        try:
            html = response.text

            content = trafilatura.extract(
                html,
                url=self.link,
                include_comments=False,
                include_tables=True,
                include_links=False,
                favor_recall=True,
                deduplicate=True,
            )

            if not content:
                logger.info(
                    f"Trafilatura found no main content for {self.link}; "
                    "page is likely a JS-rendered app or empty shell"
                )
                return "", [], ""

            title = ""
            try:
                metadata = trafilatura.extract_metadata(html)
                if metadata is not None and getattr(metadata, "title", None):
                    title = metadata.title
            except Exception as meta_err:
                logger.debug(f"Could not extract metadata for {self.link}: {meta_err}")

            # Trafilatura focuses on text; it does not collect images.
            return content, [], title

        except Exception as e:
            logger.error(f"Error parsing {self.link} with trafilatura: {e}")
            return "", [], ""

    def _fetch(self):
        """GET the page, retrying once on transient failures.

        Returns the response on success, or None when the page is
        unreachable, an error status, or too large to be worth parsing.
        """
        if self.session is None:
            logger.warning(f"No session provided for {self.link}; cannot fetch")
            return None

        for attempt in (1, 2):
            try:
                response = self.session.get(self.link, timeout=10)
            except Exception as e:
                logger.warning(f"Request failed for {self.link} (attempt {attempt}): {e}")
                if attempt == 1:
                    time.sleep(1)
                    continue
                return None

            if response.status_code in RETRYABLE_STATUS_CODES and attempt == 1:
                logger.warning(
                    f"Got HTTP {response.status_code} for {self.link}, retrying once"
                )
                time.sleep(1)
                continue

            if response.status_code >= 400:
                # Don't parse error/paywall pages as if they were content
                logger.warning(f"Got HTTP {response.status_code} for {self.link}, skipping")
                return None

            content_length = response.headers.get("Content-Length")
            if content_length:
                try:
                    length_val = int(str(content_length).strip())
                except (TypeError, ValueError):
                    length_val = None
                if length_val is not None and length_val > MAX_CONTENT_BYTES:
                    logger.warning(
                        f"Content too large for {self.link} ({content_length} bytes), skipping"
                    )
                    return None

            return response

        return None
