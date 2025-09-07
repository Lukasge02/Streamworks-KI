"""
Web Agent Service
Automated crawling und Ingestion von externen Wissensquellen
"""

import os
import json
import asyncio
import aiohttp
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re

from config import settings
from services.enterprise_document_service import EnterpriseDocumentService

class WebSource:
    """Represents an external web knowledge source"""
    
    def __init__(
        self,
        url: str,
        source_type: str = "web",  # web, confluence, sharepoint, github
        name: str = None,
        crawl_depth: int = 1,
        update_frequency: str = "weekly",  # daily, weekly, monthly
        selectors: Dict[str, str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.url = url
        self.source_type = source_type
        self.name = name or self._extract_domain_name(url)
        self.crawl_depth = crawl_depth
        self.update_frequency = update_frequency
        self.selectors = selectors or {}
        self.metadata = metadata or {}
        self.last_crawled = None
        self.status = "pending"
    
    def _extract_domain_name(self, url: str) -> str:
        """Extract clean domain name from URL"""
        domain = urlparse(url).netloc
        return domain.replace("www.", "").replace(".com", "").replace(".de", "")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "source_type": self.source_type,
            "name": self.name,
            "crawl_depth": self.crawl_depth,
            "update_frequency": self.update_frequency,
            "selectors": self.selectors,
            "metadata": self.metadata,
            "last_crawled": self.last_crawled,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebSource":
        source = cls(
            url=data["url"],
            source_type=data.get("source_type", "web"),
            name=data.get("name"),
            crawl_depth=data.get("crawl_depth", 1),
            update_frequency=data.get("update_frequency", "weekly"),
            selectors=data.get("selectors"),
            metadata=data.get("metadata")
        )
        source.last_crawled = data.get("last_crawled")
        source.status = data.get("status", "pending")
        return source

class WebAgentService:
    """Service for automated web crawling and knowledge ingestion"""
    
    def __init__(self):
        self.storage_base = Path("./storage/enterprise")
        self.web_sources_path = self.storage_base / "web_sources"
        self.metadata_path = self.storage_base / "metadata" / "web_sources"
        
        # Ensure directories exist
        for path in [self.web_sources_path, self.metadata_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        self.enterprise_doc_service = EnterpriseDocumentService()
        
        # Predefined source configurations
        self.predefined_sources = {
            "arvato_streamworks": {
                "url": "https://www.arvato-systems.de/loesungen/streamworks",
                "source_type": "web",
                "name": "Arvato StreamWorks",
                "selectors": {
                    "content": "main .content, article, .page-content",
                    "title": "h1, .page-title, .main-title",
                    "exclude": ".navigation, .footer, .sidebar, .cookie-banner"
                },
                "metadata": {
                    "industry": "data_integration",
                    "vendor": "arvato_systems",
                    "language": "de"
                }
            },
            "streamworks_docs": {
                "url": "https://docs.streamworks.cloud",
                "source_type": "web", 
                "name": "StreamWorks Documentation",
                "crawl_depth": 3,
                "selectors": {
                    "content": ".documentation-content, .doc-content, main",
                    "title": "h1, .doc-title",
                    "exclude": ".nav, .sidebar, .breadcrumbs"
                },
                "metadata": {
                    "content_type": "documentation",
                    "language": "en"
                }
            }
        }
    
    async def add_web_source(self, source_config: Dict[str, Any]) -> str:
        """Add a new web source for crawling"""
        try:
            source = WebSource(**source_config)
            source_id = self._generate_source_id(source.url)
            
            # Save source configuration
            config_file = self.metadata_path / f"{source_id}.json"
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(source.to_dict(), f, indent=2, ensure_ascii=False)
            
            print(f"✅ Added web source: {source.name} ({source_id})")
            return source_id
            
        except Exception as e:
            print(f"❌ Error adding web source: {str(e)}")
            raise Exception(f"Failed to add web source: {str(e)}")
    
    async def crawl_source(self, source_id: str) -> Dict[str, Any]:
        """Crawl a specific web source and ingest content"""
        try:
            # Load source configuration
            source = await self._load_source(source_id)
            if not source:
                raise Exception(f"Source {source_id} not found")
            
            print(f"🔍 Starting crawl of {source.name}")
            source.status = "crawling"
            await self._save_source(source_id, source)
            
            # Create session for HTTP requests
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"User-Agent": "StreamWorks-KI Agent/1.0"}
            ) as session:
                
                crawled_pages = []
                
                # Crawl starting URL
                initial_content = await self._crawl_page(session, source.url, source)
                if initial_content:
                    crawled_pages.append(initial_content)
                
                # Discover and crawl additional pages if depth > 1
                if source.crawl_depth > 1:
                    discovered_urls = await self._discover_urls(session, source.url, source)
                    for url in discovered_urls[:10]:  # Limit to 10 additional pages
                        try:
                            page_content = await self._crawl_page(session, url, source)
                            if page_content:
                                crawled_pages.append(page_content)
                        except Exception as e:
                            print(f"Warning: Failed to crawl {url}: {e}")
                            continue
                
                # Process and store crawled content
                stored_docs = 0
                for page_content in crawled_pages:
                    try:
                        await self._store_web_content(page_content, source_id, source)
                        stored_docs += 1
                    except Exception as e:
                        print(f"Warning: Failed to store content from {page_content.get('url')}: {e}")
                        continue
                
                # Update source metadata
                source.last_crawled = datetime.now().isoformat()
                source.status = "completed"
                source.metadata.update({
                    "last_crawl_results": {
                        "pages_crawled": len(crawled_pages),
                        "documents_stored": stored_docs,
                        "crawl_date": source.last_crawled
                    }
                })
                await self._save_source(source_id, source)
                
                print(f"✅ Crawl completed: {stored_docs} documents stored from {source.name}")
                
                return {
                    "source_id": source_id,
                    "source_name": source.name,
                    "pages_crawled": len(crawled_pages),
                    "documents_stored": stored_docs,
                    "status": "completed"
                }
                
        except Exception as e:
            # Update source status to error
            try:
                source.status = "error"
                source.metadata["last_error"] = str(e)
                await self._save_source(source_id, source)
            except:
                pass
            
            print(f"❌ Crawl failed for {source_id}: {str(e)}")
            raise Exception(f"Crawl failed: {str(e)}")
    
    async def _crawl_page(
        self,
        session: aiohttp.ClientSession,
        url: str,
        source: WebSource
    ) -> Optional[Dict[str, Any]]:
        """Crawl a single web page"""
        try:
            print(f"  📄 Crawling: {url}")
            
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"    ⚠️ HTTP {response.status} for {url}")
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract content using selectors
                content_text = self._extract_content(soup, source.selectors)
                
                if len(content_text.strip()) < 100:  # Skip pages with minimal content
                    return None
                
                # Extract title
                title = self._extract_title(soup, source.selectors)
                
                return {
                    "url": url,
                    "title": title,
                    "content": content_text,
                    "crawl_date": datetime.now().isoformat(),
                    "content_hash": hashlib.sha256(content_text.encode()).hexdigest()
                }
                
        except Exception as e:
            print(f"    ❌ Error crawling {url}: {str(e)}")
            return None
    
    def _extract_content(self, soup: BeautifulSoup, selectors: Dict[str, str]) -> str:
        """Extract main content from HTML using CSS selectors"""
        try:
            # Remove unwanted elements
            exclude_selector = selectors.get("exclude", "")
            if exclude_selector:
                for element in soup.select(exclude_selector):
                    element.decompose()
            
            # Extract main content
            content_selector = selectors.get("content", "main, article, .content")
            content_elements = soup.select(content_selector)
            
            if not content_elements:
                # Fallback: use body content
                content_elements = soup.select("body")
            
            # Combine text from all content elements
            content_parts = []
            for element in content_elements:
                text = element.get_text(separator=" ", strip=True)
                if text:
                    content_parts.append(text)
            
            content = " ".join(content_parts)
            
            # Clean up text
            content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
            content = re.sub(r'\n+', '\n', content)  # Normalize line breaks
            
            return content.strip()
            
        except Exception as e:
            print(f"    Warning: Content extraction failed: {e}")
            return soup.get_text(separator=" ", strip=True)
    
    def _extract_title(self, soup: BeautifulSoup, selectors: Dict[str, str]) -> str:
        """Extract page title using selectors"""
        try:
            title_selector = selectors.get("title", "h1")
            title_elements = soup.select(title_selector)
            
            if title_elements:
                return title_elements[0].get_text(strip=True)
            
            # Fallback to HTML title
            title_tag = soup.find("title")
            if title_tag:
                return title_tag.get_text(strip=True)
            
            return "Untitled"
            
        except Exception as e:
            return "Untitled"
    
    async def _discover_urls(
        self,
        session: aiohttp.ClientSession,
        base_url: str,
        source: WebSource
    ) -> List[str]:
        """Discover additional URLs to crawl from the base page"""
        try:
            async with session.get(base_url) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                discovered_urls = set()
                base_domain = urlparse(base_url).netloc
                
                # Find all links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    
                    # Convert relative URLs to absolute
                    full_url = urljoin(base_url, href)
                    parsed_url = urlparse(full_url)
                    
                    # Only include links from the same domain
                    if parsed_url.netloc == base_domain:
                        # Filter out common non-content URLs
                        if not any(skip in full_url.lower() for skip in [
                            'login', 'register', 'cart', 'checkout', 'admin',
                            '.pdf', '.jpg', '.png', '.gif', '.css', '.js',
                            '#', '?', 'mailto:', 'tel:'
                        ]):
                            discovered_urls.add(full_url)
                
                return list(discovered_urls)
                
        except Exception as e:
            print(f"    Warning: URL discovery failed: {e}")
            return []
    
    async def _store_web_content(
        self,
        page_content: Dict[str, Any],
        source_id: str,
        source: WebSource
    ) -> str:
        """Store crawled web content as document in enterprise storage"""
        try:
            # Create temporary file with web content
            temp_dir = Path("/tmp/streamworks_webcrawl")
            temp_dir.mkdir(exist_ok=True)
            
            # Generate filename from URL
            url_hash = hashlib.sha256(page_content["url"].encode()).hexdigest()[:8]
            filename = f"{source.name}_{url_hash}.md"
            temp_file = temp_dir / filename
            
            # Create markdown content
            markdown_content = f"""# {page_content['title']}

**Source:** {page_content['url']}  
**Crawled:** {page_content['crawl_date']}  
**Source Type:** {source.source_type}

---

{page_content['content']}

---

**Metadata:**
- Source: {source.name}
- URL: {page_content['url']}
- Content Hash: {page_content['content_hash']}
"""
            
            # Save temporary file
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            
            # Store using enterprise document service
            doc_id, document = await self.enterprise_doc_service.store_document(
                file_path=str(temp_file),
                filename=filename,
                doctype="web_source",
                tags=[source.source_type, source.name.lower().replace(" ", "_")],
                visibility=["internal", "web_crawl"],
                language=source.metadata.get("language", "auto"),
                metadata={
                    "source_url": page_content["url"],
                    "source_id": source_id,
                    "source_name": source.name,
                    "crawl_date": page_content["crawl_date"],
                    "content_hash": page_content["content_hash"],
                    "web_agent": True
                }
            )
            
            # Clean up temporary file
            if temp_file.exists():
                temp_file.unlink()
            
            print(f"    ✅ Stored: {page_content['title'][:50]}...")
            return doc_id
            
        except Exception as e:
            print(f"    ❌ Storage failed for {page_content.get('url')}: {str(e)}")
            raise
    
    async def setup_predefined_sources(self) -> List[str]:
        """Setup predefined knowledge sources"""
        try:
            source_ids = []
            
            for source_key, source_config in self.predefined_sources.items():
                source_id = await self.add_web_source(source_config)
                source_ids.append(source_id)
            
            print(f"✅ Setup {len(source_ids)} predefined sources")
            return source_ids
            
        except Exception as e:
            print(f"❌ Error setting up predefined sources: {str(e)}")
            raise
    
    async def run_scheduled_crawls(self) -> Dict[str, Any]:
        """Run scheduled crawls for all active sources"""
        try:
            results = {
                "crawls_completed": 0,
                "crawls_failed": 0,
                "total_documents": 0,
                "details": []
            }
            
            # Load all sources
            sources = await self.list_sources()
            
            for source_info in sources:
                source_id = source_info["id"]
                
                try:
                    # Check if crawl is due
                    if await self._is_crawl_due(source_id):
                        print(f"⏰ Scheduled crawl for {source_info['name']}")
                        crawl_result = await self.crawl_source(source_id)
                        
                        results["crawls_completed"] += 1
                        results["total_documents"] += crawl_result["documents_stored"]
                        results["details"].append(crawl_result)
                    
                except Exception as e:
                    print(f"❌ Scheduled crawl failed for {source_id}: {str(e)}")
                    results["crawls_failed"] += 1
                    results["details"].append({
                        "source_id": source_id,
                        "source_name": source_info.get("name", "Unknown"),
                        "status": "failed",
                        "error": str(e)
                    })
            
            return results
            
        except Exception as e:
            print(f"❌ Scheduled crawls failed: {str(e)}")
            raise
    
    async def list_sources(self) -> List[Dict[str, Any]]:
        """List all configured web sources"""
        try:
            sources = []
            
            if not self.metadata_path.exists():
                return sources
            
            for config_file in self.metadata_path.glob("*.json"):
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        source_data = json.load(f)
                    
                    source_id = config_file.stem
                    source_info = {
                        "id": source_id,
                        "name": source_data.get("name", "Unknown"),
                        "url": source_data.get("url"),
                        "source_type": source_data.get("source_type", "web"),
                        "status": source_data.get("status", "pending"),
                        "last_crawled": source_data.get("last_crawled"),
                        "update_frequency": source_data.get("update_frequency", "weekly")
                    }
                    
                    sources.append(source_info)
                    
                except Exception as e:
                    print(f"Warning: Could not load source from {config_file}: {e}")
                    continue
            
            return sources
            
        except Exception as e:
            print(f"❌ Error listing sources: {str(e)}")
            return []
    
    def _generate_source_id(self, url: str) -> str:
        """Generate unique source ID from URL"""
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:12]
        domain = urlparse(url).netloc.replace("www.", "").replace(".", "_")
        return f"{domain}_{url_hash}"
    
    async def _load_source(self, source_id: str) -> Optional[WebSource]:
        """Load source configuration from file"""
        try:
            config_file = self.metadata_path / f"{source_id}.json"
            if not config_file.exists():
                return None
            
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return WebSource.from_dict(data)
            
        except Exception as e:
            print(f"❌ Error loading source {source_id}: {str(e)}")
            return None
    
    async def _save_source(self, source_id: str, source: WebSource) -> None:
        """Save source configuration to file"""
        try:
            config_file = self.metadata_path / f"{source_id}.json"
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(source.to_dict(), f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Error saving source {source_id}: {str(e)}")
            raise
    
    async def _is_crawl_due(self, source_id: str) -> bool:
        """Check if a source is due for crawling based on update frequency"""
        try:
            source = await self._load_source(source_id)
            if not source or not source.last_crawled:
                return True
            
            last_crawl = datetime.fromisoformat(source.last_crawled)
            now = datetime.now()
            
            frequency_map = {
                "daily": timedelta(days=1),
                "weekly": timedelta(weeks=1),
                "monthly": timedelta(days=30)
            }
            
            interval = frequency_map.get(source.update_frequency, timedelta(weeks=1))
            return now >= last_crawl + interval
            
        except Exception as e:
            print(f"Warning: Could not check crawl schedule for {source_id}: {e}")
            return True