from mcp.server.fastmcp import FastMCP
import json
import requests
import time
from typing import List, Dict, Any
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create MCP server
mcp = FastMCP("AIVCResearch")

class AIVCResearcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        # Get Brave Search API key from environment variable
        self.brave_api_key = os.getenv('BRAVE_SEARCH_API_KEY')
        if not self.brave_api_key:
            print("Warning: BRAVE_SEARCH_API_KEY environment variable not set. Search functionality will be limited.")
    
    def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """Search the web using Brave Search API"""
        try:
            if not self.brave_api_key:
                return self._fallback_search(query, num_results)
            
            # Using Brave Search API
            search_url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip',
                'X-Subscription-Token': self.brave_api_key
            }
            params = {
                'q': query,
                'count': num_results,
                'offset': 0,
                'mkt': 'en-US',
                'safesearch': 'moderate',
                'freshness': 'pw',  # Past week for recent results
                'text_decorations': False,
                'spellcheck': True
            }
            
            response = self.session.get(search_url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Extract search results
            if 'web' in data and 'results' in data['web']:
                for result in data['web']['results'][:num_results]:
                    results.append({
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'snippet': result.get('description', '')
                    })
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Brave Search API error: {e}")
            return self._fallback_search(query, num_results)
        except Exception as e:
            print(f"Search error: {e}")
            return self._fallback_search(query, num_results)
    
    def _fallback_search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """Fallback search - return empty results and let user know Brave API is needed"""
        print("Brave Search API key not available. Please set BRAVE_SEARCH_API_KEY environment variable.")
        return []
    
    def research_vc(self, vc_name: str) -> Dict[str, Any]:
        """Research a specific VC firm"""
        # Search for the VC firm
        search_queries = [
            f"{vc_name} venture capital AI investments",
            f"{vc_name} portfolio companies artificial intelligence",
            f"{vc_name} VC firm profile"
        ]
        
        all_results = []
        for query in search_queries:
            results = self.search_web(query, num_results=3)
            all_results.extend(results)
            time.sleep(1)  # Be respectful to the search engine
        
        # Remove duplicates
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        return {
            'vc_name': vc_name,
            'search_results': unique_results[:10],  # Return top 10 unique results
            'urls_for_fetching': [result['url'] for result in unique_results[:5]]  # Top 5 URLs for content fetching
        }

# Initialize researcher
researcher = AIVCResearcher()

@mcp.tool()
def search_ai_vcs(query: str) -> str:
    """Search for AI venture capital firms based on a query"""
    try:
        results = researcher.search_web(f"{query} AI venture capital firms", num_results=10)
        
        if not results:
            return "No search results found. Make sure BRAVE_SEARCH_API_KEY is set."
        
        output = [f"Search Results for: {query}\n" + "="*50]
        
        for i, result in enumerate(results, 1):
            output.append(f"{i}. {result['title']}")
            output.append(f"   URL: {result['url']}")
            if result['snippet']:
                output.append(f"   Snippet: {result['snippet']}")
            output.append("")
        
        return "\n".join(output)
    
    except Exception as e:
        return f"Error searching: {str(e)}"

@mcp.tool()
def get_vc_urls(vc_name: str) -> str:
    """Get URLs for a VC firm that can be used with web_fetch tool"""
    try:
        print(f"Searching for {vc_name} URLs...")
        research_data = researcher.research_vc(vc_name)
        
        output = [f"URLs FOR {research_data['vc_name'].upper()}"]
        output.append("=" * 50)
        output.append("")
        output.append("Use these URLs with the web_fetch tool to get detailed content:")
        output.append("")
        
        for i, url in enumerate(research_data['urls_for_fetching'], 1):
            output.append(f"{i}. {url}")
        
        output.append("")
        output.append("All search results:")
        for i, result in enumerate(research_data['search_results'], 1):
            output.append(f"{i}. {result['title']}")
            output.append(f"   URL: {result['url']}")
            if result['snippet']:
                output.append(f"   Snippet: {result['snippet']}")
            output.append("")
        
        return "\n".join(output)
    
    except Exception as e:
        return f"Error getting VC URLs: {str(e)}"

@mcp.tool()
def research_vc_firm(vc_name: str) -> str:
    """Research a specific VC firm and provide URLs for detailed content fetching"""
    try:
        print(f"Researching {vc_name}...")
        research_data = researcher.research_vc(vc_name)
        
        # Compile report
        report = []
        report.append(f"RESEARCH REPORT: {research_data['vc_name']}")
        report.append("=" * 60)
        report.append("")
        
        report.append("INSTRUCTIONS:")
        report.append("Use the web_fetch tool on the URLs below to get detailed content.")
        report.append("")
        
        # Add URLs for fetching
        report.append("TOP URLs FOR CONTENT FETCHING:")
        report.append("-" * 35)
        for i, url in enumerate(research_data['urls_for_fetching'], 1):
            report.append(f"{i}. {url}")
        report.append("")
        
        # Add all search results
        report.append("ALL SEARCH RESULTS:")
        report.append("-" * 20)
        for i, result in enumerate(research_data['search_results'], 1):
            report.append(f"{i}. {result['title']}")
            report.append(f"   URL: {result['url']}")
            if result['snippet']:
                report.append(f"   Snippet: {result['snippet']}")
            report.append("")
        
        return "\n".join(report)
    
    except Exception as e:
        return f"Error researching VC firm: {str(e)}"

@mcp.tool()
def get_vc_portfolio_urls(vc_name: str) -> str:
    """Get URLs about a VC firm's portfolio for use with web_fetch"""
    try:
        query = f"{vc_name} portfolio companies investments list"
        results = researcher.search_web(query, num_results=8)
        
        if not results:
            return f"No portfolio URLs found for {vc_name}. Check if BRAVE_SEARCH_API_KEY is set."
        
        # Compile portfolio URL report
        report = []
        report.append(f"PORTFOLIO RESEARCH URLs: {vc_name}")
        report.append("=" * 50)
        report.append("")
        report.append("Use these URLs with web_fetch tool to get portfolio details:")
        report.append("")
        
        for i, result in enumerate(results, 1):
            report.append(f"{i}. {result['title']}")
            report.append(f"   URL: {result['url']}")
            if result['snippet']:
                report.append(f"   Snippet: {result['snippet']}")
            report.append("")
        
        return "\n".join(report)
    
    except Exception as e:
        return f"Error getting portfolio URLs: {str(e)}"

@mcp.tool()
def compare_vc_firms(vc_names: str) -> str:
    """Get comparison URLs for multiple VC firms (provide comma-separated list)"""
    try:
        vc_list = [name.strip() for name in vc_names.split(',')]
        
        comparison_data = {}
        for vc_name in vc_list:
            print(f"Getting URLs for {vc_name}...")
            research_data = researcher.research_vc(vc_name)
            comparison_data[vc_name] = research_data
            time.sleep(1)  # Be respectful
        
        # Compile comparison report
        report = []
        report.append(f"COMPARISON URLs: {' vs '.join(vc_list)}")
        report.append("=" * 80)
        report.append("")
        report.append("Use web_fetch on these URLs to get detailed comparison data:")
        report.append("")
        
        for vc_name, data in comparison_data.items():
            report.append(f"\n{vc_name.upper()}")
            report.append("-" * len(vc_name))
            
            report.append("Top URLs to fetch:")
            for url in data['urls_for_fetching']:
                report.append(f"  • {url}")
            
            report.append(f"\nAll search results ({len(data['search_results'])} found):")
            for result in data['search_results'][:3]:  # Show top 3
                report.append(f"  • {result['title']}")
                report.append(f"    {result['url']}")
            report.append("")
        
        return "\n".join(report)
    
    except Exception as e:
        return f"Error comparing VC firms: {str(e)}"

if __name__ == "__main__":
    print("Starting AI VC Research MCP Server...")
    print("Server will communicate via stdio")
    print("Press Ctrl+C to stop")
    mcp.run()