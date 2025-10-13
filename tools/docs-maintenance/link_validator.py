#!/usr/bin/env python3
"""
PdaNet Linux - Link Validator
Advanced link validation with retry logic and detailed reporting
"""

import asyncio
import json
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import aiohttp


@dataclass
class LinkResult:
    """Result of link validation"""

    url: str
    status: str  # 'valid', 'broken', 'timeout', 'redirect', 'unknown'
    status_code: int | None
    final_url: str | None
    response_time: float | None
    error_message: str | None
    source_file: str
    context: str


@dataclass
class ValidationReport:
    """Link validation report"""

    timestamp: str
    total_links: int
    valid_links: int
    broken_links: int
    redirected_links: int
    timeout_links: int
    internal_links: int
    external_links: int
    results: list[LinkResult]
    summary: dict[str, int]


class LinkValidator:
    """Advanced link validator with async processing"""

    def __init__(self, project_root: str, timeout: float = 10.0, max_concurrent: int = 10):
        self.project_root = Path(project_root)
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.session = None

        # User agent for requests
        self.user_agent = "PdaNet-Link-Validator/1.0 (Documentation Maintenance)"

        # Patterns for different link types
        self.link_patterns = [
            # Markdown links: [text](url)
            (r"\[([^\]]*)\]\(([^)]+)\)", "markdown"),
            # HTML links: <a href="url">
            (r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>', "html"),
            # Reference links: [text][ref] and [ref]: url
            (r"\[([^\]]+)\]:\s*([^\s]+)", "reference"),
            # Auto links: <url>
            (r"<(https?://[^>]+)>", "autolink"),
            # Plain URLs
            (r"(?:^|\s)(https?://[^\s]+)", "plain"),
        ]

    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=self.max_concurrent)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(
            connector=connector, timeout=timeout, headers={"User-Agent": self.user_agent}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def extract_links_from_file(self, file_path: Path) -> list[tuple[str, str, str]]:
        """Extract all links from a markdown/text file"""
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            return []

        links = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            for pattern, link_type in self.link_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    if link_type in ["markdown", "html"]:
                        url = match.group(2) if len(match.groups()) > 1 else match.group(1)
                        text = match.group(1) if len(match.groups()) > 1 else "link"
                    elif link_type == "reference":
                        url = match.group(2)
                        text = match.group(1)
                    else:
                        url = match.group(1)
                        text = "link"

                    # Clean up URL
                    url = url.strip()
                    if url and not url.startswith("#"):  # Skip anchors
                        context = f"Line {line_num}: {line.strip()[:50]}..."
                        links.append((url, text, context))

        return links

    def categorize_link(self, url: str) -> str:
        """Categorize link as internal or external"""
        if url.startswith(("http://", "https://")) or url.startswith(("mailto:", "tel:", "ftp:")):
            return "external"
        else:
            return "internal"

    async def validate_external_link(self, url: str, source_file: str, context: str) -> LinkResult:
        """Validate an external link"""
        start_time = time.time()

        try:
            # Handle relative URLs that might be malformed
            if not url.startswith(("http://", "https://")):
                if url.startswith("//"):
                    url = "https:" + url
                else:
                    return LinkResult(
                        url=url,
                        status="broken",
                        status_code=None,
                        final_url=None,
                        response_time=None,
                        error_message="Invalid URL format",
                        source_file=source_file,
                        context=context,
                    )

            async with self.session.head(url, allow_redirects=True) as response:
                response_time = time.time() - start_time

                if response.status == 200:
                    status = "redirect" if str(response.url) != url else "valid"
                    return LinkResult(
                        url=url,
                        status=status,
                        status_code=response.status,
                        final_url=str(response.url),
                        response_time=response_time,
                        error_message=None,
                        source_file=source_file,
                        context=context,
                    )
                elif response.status in [301, 302, 303, 307, 308]:
                    return LinkResult(
                        url=url,
                        status="redirect",
                        status_code=response.status,
                        final_url=str(response.url),
                        response_time=response_time,
                        error_message=None,
                        source_file=source_file,
                        context=context,
                    )
                else:
                    return LinkResult(
                        url=url,
                        status="broken",
                        status_code=response.status,
                        final_url=None,
                        response_time=response_time,
                        error_message=f"HTTP {response.status}",
                        source_file=source_file,
                        context=context,
                    )

        except TimeoutError:
            return LinkResult(
                url=url,
                status="timeout",
                status_code=None,
                final_url=None,
                response_time=self.timeout,
                error_message="Request timeout",
                source_file=source_file,
                context=context,
            )
        except Exception as e:
            return LinkResult(
                url=url,
                status="broken",
                status_code=None,
                final_url=None,
                response_time=time.time() - start_time,
                error_message=str(e),
                source_file=source_file,
                context=context,
            )

    def validate_internal_link(self, url: str, source_file: str, context: str) -> LinkResult:
        """Validate an internal link"""
        source_path = Path(source_file)

        # Handle different internal link formats
        if url.startswith("/"):
            # Absolute path from project root
            target_path = self.project_root / url[1:]
        else:
            # Relative path from source file directory
            target_path = source_path.parent / url

        # Remove fragment identifiers
        if "#" in url:
            url_part = url.split("#")[0]
            if url_part:
                target_path = (
                    source_path.parent / url_part
                    if not url.startswith("/")
                    else self.project_root / url_part[1:]
                )

        # Normalize path
        try:
            target_path = target_path.resolve()
        except Exception:
            return LinkResult(
                url=url,
                status="broken",
                status_code=None,
                final_url=None,
                response_time=0.0,
                error_message="Invalid path",
                source_file=source_file,
                context=context,
            )

        # Check if file exists
        if target_path.exists():
            if target_path.is_file():
                return LinkResult(
                    url=url,
                    status="valid",
                    status_code=200,
                    final_url=str(target_path.relative_to(self.project_root)),
                    response_time=0.0,
                    error_message=None,
                    source_file=source_file,
                    context=context,
                )
            else:
                return LinkResult(
                    url=url,
                    status="broken",
                    status_code=None,
                    final_url=None,
                    response_time=0.0,
                    error_message="Target is directory, not file",
                    source_file=source_file,
                    context=context,
                )
        else:
            return LinkResult(
                url=url,
                status="broken",
                status_code=404,
                final_url=None,
                response_time=0.0,
                error_message="File not found",
                source_file=source_file,
                context=context,
            )

    async def validate_links_batch(
        self, links: list[tuple[str, str, str, str]]
    ) -> list[LinkResult]:
        """Validate a batch of links"""
        tasks = []

        for url, source_file, context, link_type in links:
            if link_type == "external":
                task = self.validate_external_link(url, source_file, context)
                tasks.append(task)
            else:
                # Internal links are validated synchronously
                result = self.validate_internal_link(url, source_file, context)
                tasks.append(asyncio.create_task(asyncio.coroutine(lambda r=result: r)()))

        return await asyncio.gather(*tasks, return_exceptions=True)

    async def validate_all_links(self) -> ValidationReport:
        """Validate all links in the project"""
        print("🔍 Discovering documentation files...")

        # Find all documentation files
        doc_files = []
        for pattern in ["*.md", "*.txt", "*.rst"]:
            doc_files.extend(self.project_root.rglob(pattern))

        # Filter out hidden directories except .claude
        filtered_files = []
        for file_path in doc_files:
            if any(part.startswith(".") and part != ".claude" for part in file_path.parts):
                continue
            filtered_files.append(file_path)

        print(f"📝 Extracting links from {len(filtered_files)} files...")

        all_links = []
        for file_path in filtered_files:
            file_links = self.extract_links_from_file(file_path)
            for url, text, context in file_links:
                link_type = self.categorize_link(url)
                relative_path = str(file_path.relative_to(self.project_root))
                all_links.append((url, relative_path, context, link_type))

        # Remove duplicates while preserving source information
        unique_links = []
        seen = set()
        for url, source_file, context, link_type in all_links:
            key = (url, source_file)
            if key not in seen:
                seen.add(key)
                unique_links.append((url, source_file, context, link_type))

        print(f"🔗 Found {len(unique_links)} unique links to validate...")

        # Separate internal and external links
        internal_links = [
            (url, sf, ctx, lt) for url, sf, ctx, lt in unique_links if lt == "internal"
        ]
        external_links = [
            (url, sf, ctx, lt) for url, sf, ctx, lt in unique_links if lt == "external"
        ]

        print(f"  • Internal links: {len(internal_links)}")
        print(f"  • External links: {len(external_links)}")

        # Validate all links
        print("✅ Validating links...")
        results = []

        # Process in batches to avoid overwhelming servers
        batch_size = self.max_concurrent
        for i in range(0, len(unique_links), batch_size):
            batch = unique_links[i : i + batch_size]
            print(
                f"  Processing batch {i // batch_size + 1}/{(len(unique_links) + batch_size - 1) // batch_size}"
            )

            batch_results = await self.validate_links_batch(batch)
            for result in batch_results:
                if isinstance(result, LinkResult):
                    results.append(result)
                elif isinstance(result, Exception):
                    print(f"  Error processing link: {result}")

            # Small delay between batches
            if i + batch_size < len(unique_links):
                await asyncio.sleep(1.0)

        # Generate summary statistics
        summary = {
            "valid": sum(1 for r in results if r.status == "valid"),
            "broken": sum(1 for r in results if r.status == "broken"),
            "redirect": sum(1 for r in results if r.status == "redirect"),
            "timeout": sum(1 for r in results if r.status == "timeout"),
            "internal": sum(1 for r in results if self.categorize_link(r.url) == "internal"),
            "external": sum(1 for r in results if self.categorize_link(r.url) == "external"),
        }

        return ValidationReport(
            timestamp=datetime.now().isoformat(),
            total_links=len(results),
            valid_links=summary["valid"],
            broken_links=summary["broken"],
            redirected_links=summary["redirect"],
            timeout_links=summary["timeout"],
            internal_links=summary["internal"],
            external_links=summary["external"],
            results=results,
            summary=summary,
        )

    def save_report(self, report: ValidationReport, output_path: str) -> None:
        """Save validation report to JSON file"""
        with open(output_path, "w") as f:
            json.dump(asdict(report), f, indent=2, default=str)

    def print_summary(self, report: ValidationReport) -> None:
        """Print validation summary"""
        print("\n" + "=" * 50)
        print("🔗 LINK VALIDATION SUMMARY")
        print("=" * 50)

        print(f"📊 Total links validated: {report.total_links}")
        print(f"  • Internal links: {report.internal_links}")
        print(f"  • External links: {report.external_links}")

        print("\n✅ Validation Results:")
        print(f"  • Valid: {report.valid_links} ({report.valid_links/report.total_links*100:.1f}%)")
        print(
            f"  • Broken: {report.broken_links} ({report.broken_links/report.total_links*100:.1f}%)"
        )
        print(
            f"  • Redirected: {report.redirected_links} ({report.redirected_links/report.total_links*100:.1f}%)"
        )
        print(
            f"  • Timeout: {report.timeout_links} ({report.timeout_links/report.total_links*100:.1f}%)"
        )

        if report.broken_links > 0:
            print(f"\n❌ Broken Links ({report.broken_links}):")
            broken_results = [r for r in report.results if r.status == "broken"]
            for result in broken_results[:10]:  # Show first 10
                print(f"  • {result.url}")
                print(f"    Source: {result.source_file}")
                print(f"    Error: {result.error_message}")

            if len(broken_results) > 10:
                print(f"    ... and {len(broken_results) - 10} more")

        if report.redirected_links > 0:
            print(f"\n🔄 Redirected Links ({report.redirected_links}):")
            redirect_results = [r for r in report.results if r.status == "redirect"]
            for result in redirect_results[:5]:  # Show first 5
                print(f"  • {result.url} → {result.final_url}")
                print(f"    Source: {result.source_file}")


async def main():
    """Main function for CLI usage"""
    import sys

    if len(sys.argv) != 2:
        print("Usage: python link_validator.py <project_root>")
        sys.exit(1)

    project_root = sys.argv[1]

    async with LinkValidator(project_root) as validator:
        report = await validator.validate_all_links()

        # Save detailed report
        output_dir = Path(project_root) / "tools" / "docs-maintenance" / "reports"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_dir / f"link_validation_{timestamp}.json"
        validator.save_report(report, str(report_file))

        # Print summary
        validator.print_summary(report)
        print(f"\n📄 Detailed report saved to: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())
