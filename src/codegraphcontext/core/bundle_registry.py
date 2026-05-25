# src/codegraphcontext/core/bundle_registry.py
import requests
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


def _github_headers() -> dict:
    """Return GitHub API headers, including auth token if available."""
    import os
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    return headers

def _get_manifest_url() -> str:
    import os
    hf_repo = os.environ.get("HF_REGISTRY_REPO") or "codegraphcontext/bundles"
    return f"https://huggingface.co/datasets/{hf_repo}/raw/main/manifest.json"

REGISTRY_API_URL = "https://api.github.com/repos/CodeGraphContext/CodeGraphContext/releases"

class BundleRegistry:
    """
    Core logic for interacting with the CodeGraphContext bundle registry.
    Handles fetching metadata, searching, and downloading bundles without CLI dependencies.
    """

    @staticmethod
    def fetch_available_bundles() -> List[Dict[str, Any]]:
        """
        Fetch all available bundles from GitHub Releases and the on-demand manifest.
        Returns a list of bundle dictionaries with metadata.
        Preserves all versions - no deduplication.
        """
        all_bundles = []
        
        # 1. Fetch on-demand bundles from manifest
        try:
            response = requests.get(_get_manifest_url(), headers=_github_headers(), timeout=10)
            if response.status_code == 200:
                manifest = response.json()
                if manifest.get('bundles'):
                    for bundle in manifest['bundles']:
                        bundle['source'] = 'on-demand'
                        # Ensure bundle has a full_name field (with version info)
                        if 'bundle_name' in bundle:
                            # Extract full name without .cgc extension
                            bundle['full_name'] = bundle['bundle_name'].replace('.cgc', '')
                        all_bundles.append(bundle)
        except Exception as e:
            logger.warning(f"Could not fetch on-demand bundles from manifest: {e}")
        
        # 2. Fetch weekly pre-indexed bundles
        try:
            response = requests.get(REGISTRY_API_URL, headers=_github_headers(), timeout=10)
            if response.status_code == 200:
                releases = response.json()
                
                # Find weekly releases (bundles-YYYYMMDD pattern)
                weekly_releases = [r for r in releases if r['tag_name'].startswith('bundles-') and r['tag_name'] != 'bundles-latest']
                
                if weekly_releases:
                    # Get the most recent weekly release
                    latest_weekly = weekly_releases[0]
                    
                    for asset in latest_weekly.get('assets', []):
                        if asset['name'].endswith('.cgc'):
                            # Full bundle name without extension
                            full_name = asset['name'].replace('.cgc', '')
                            
                            # Parse bundle name
                            # Parse bundle name (expects double-underscore layout)
                            clean_name = full_name
                            if clean_name.startswith("cgc__"):
                                clean_name = clean_name[5:]
                            parts = clean_name.split('__')
                            if len(parts) >= 2:
                                repo_name = parts[1]
                                repo_path = f"{parts[0]}/{parts[1]}"
                                version = parts[2] if len(parts) > 2 else 'latest'
                                commit = parts[3] if len(parts) > 3 else 'unknown'
                            else:
                                repo_name = full_name
                                repo_path = full_name
                                version = 'latest'
                                commit = 'unknown'

                            bundle = {
                                'name': repo_name,  # Base package name
                                'full_name': full_name,  # Complete name with version
                                'repo': repo_path,
                                'bundle_name': asset['name'],
                                'version': version,
                                'commit': commit,
                                'size_bytes': asset.get('size', 0),
                                'size': f"{asset['size'] / 1024 / 1024:.1f}MB",
                                'download_url': asset['browser_download_url'],
                                'generated_at': asset['updated_at'],
                                'source': 'weekly'
                            }
                            all_bundles.append(bundle)
        except Exception as e:
            logger.warning(f"Could not fetch weekly bundles from GitHub API: {e}")
        
        # Normalize all bundles to have required fields
        for bundle in all_bundles:
            # Ensure 'name' field exists (base package name)
            if 'name' not in bundle:
                repo = bundle.get('repo', '')
                if '/' in repo:
                    bundle['name'] = repo.split('/')[-1]
                else:
                    # Extract from full_name or bundle_name
                    full_name = bundle.get('full_name', bundle.get('bundle_name', 'unknown'))
                    clean_name = full_name
                    if clean_name.startswith("cgc__"):
                        clean_name = clean_name[5:]
                    parts = clean_name.split('__')
                    bundle['name'] = parts[1] if len(parts) > 1 else parts[0]
            
            # Ensure 'full_name' exists
            if 'full_name' not in bundle:
                bundle['full_name'] = bundle.get('bundle_name', bundle.get('name', 'unknown')).replace('.cgc', '')
        
        return all_bundles

    @staticmethod
    def find_bundle_download_info(name: str) -> Tuple[Optional[str], Optional[Dict[str, Any]], str]:
        """
        Find a download URL and metadata for a bundle by name.
        
        Strategies:
        1. Exact match on full_name (e.g., 'flask-main-abc123')
        2. Match on base name (e.g., 'flask') - returns most recent version
        
        Returns:
            (download_url, bundle_metadata, error_message)
        """
        bundles = BundleRegistry.fetch_available_bundles()
        
        if not bundles:
            return None, None, "Could not fetch bundle registry."
        
        name_lower = name.lower()
        
        # Strategy 1: Exact match on full_name
        for b in bundles:
            if b.get('full_name', '').lower() == name_lower:
                url = b.get('download_url')
                if url:
                    return url, b, ""
                return None, b, f"No download URL found for bundle '{name}'"
        
        # Strategy 2: Match base package name (most recent)
        matching_bundles = []
        for b in bundles:
            if b.get('name', '').lower() == name_lower:
                matching_bundles.append(b)
        
        if matching_bundles:
            # Sort by timestamp (newest first)
            matching_bundles.sort(key=lambda x: x.get('generated_at', ''), reverse=True)
            bundle = matching_bundles[0]
            url = bundle.get('download_url')
            if url:
                return url, bundle, ""
            return None, bundle, f"No download URL found for bundle '{name}'"
            
        return None, None, f"Bundle '{name}' not found in registry."

    @staticmethod
    def download_file(url: str, output_path: Path, progress_callback=None) -> bool:
        """
        Download a file from a URL to a local path.
        
        Args:
            url: The URL to download from
            output_path: Local path to save the file
            progress_callback: Optional callable(chunk_size) to report progress
            
        Returns:
            True if successful, raises exception otherwise
        """
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        if progress_callback:
                            progress_callback(len(chunk))
            return True
        except Exception as e:
            # Clean up partial file
            if output_path.exists():
                output_path.unlink()
            raise e
