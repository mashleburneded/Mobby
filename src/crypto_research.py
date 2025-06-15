# src/crypto_research.py
import logging
import requests
from config import config

logger = logging.getLogger(__name__)

def search_protocol(protocol_name: str) -> dict:
    """Search for a protocol - alias for search_protocol_by_name"""
    return search_protocol_by_name(protocol_name)

def search_protocol_by_name(protocol_name: str) -> dict:
    """Search for a specific protocol by name"""
    try:
        url = "https://api.llama.fi/protocols"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Search for protocol by name (case insensitive)
        protocol_name_lower = protocol_name.lower()
        for protocol in data:
            name = protocol.get('name', '').lower()
            slug = protocol.get('slug', '').lower()
            
            if (protocol_name_lower in name or 
                protocol_name_lower in slug or 
                name in protocol_name_lower or
                slug in protocol_name_lower):
                return protocol
        
        return {"success": False, "message": f"Protocol '{protocol_name}' not found"}
    except Exception as e:
        logger.error(f"Error searching for protocol {protocol_name}: {e}")
        return {"success": False, "message": f"Error searching for protocol: {e}"}

def query_defillama(data_type: str, slug: str = None, protocol_name: str = None) -> str:
    """Query DeFiLlama API for various data types"""
    base_url = "https://api.llama.fi"
    
    # If protocol_name is provided, search for it first
    if protocol_name and not slug:
        protocol = search_protocol_by_name(protocol_name)
        if protocol:
            slug = protocol.get('slug')
        else:
            return f"❌ Protocol '{protocol_name}' not found on DeFiLlama. Try checking the spelling or use a different name."
    
    # Enhanced endpoints with more DeFiLlama API features - FIXED ENDPOINTS
    endpoints = {
        'tvl': f"/tvl/{slug}" if slug else "/charts",
        'revenue': f"/summary/fees/{slug}?dataType=dailyRevenue" if slug else "/overview/fees",
        'volume': f"/summary/dexs/{slug}" if slug else "/overview/dexs",
        'protocols': "/protocols",
        'chains': "/chains",
        'yields': "/pools",  # Fixed: was /yields/pools
        'stablecoins': "/stablecoins",  # Fixed: removed includePrices param
        'bridges': "/bridges",  # Fixed: was /bridges2
        'fees': f"/summary/fees/{slug}" if slug else "/overview/fees",
        'raises': "/raises"  # Fixed: removed slug handling
    }
    
    if data_type not in endpoints:
        return f"❌ Invalid data type. Available: {', '.join(endpoints.keys())}"
    
    try:
        url = f"{base_url}{endpoints[data_type]}"
        logger.info(f"Querying DeFiLlama: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
        
        # Handle empty responses
        if not response.content:
            return f"❌ No data returned from DeFiLlama for {data_type}"
        
        try:
            data = response.json()
        except ValueError as e:
            logger.error(f"JSON decode error for {data_type}: {e}")
            return f"❌ Invalid response format from DeFiLlama for {data_type}"
        
        # Format response based on data type
        if data_type == 'protocols':
            if not data:
                return "No protocols found."
            
            # If searching for specific protocol, show detailed info
            if protocol_name or slug:
                # Find the specific protocol
                target_protocol = None
                if protocol_name:
                    target_protocol = search_protocol_by_name(protocol_name)
                else:
                    # Find by slug
                    for protocol in data:
                        if protocol.get('slug') == slug:
                            target_protocol = protocol
                            break
                
                if target_protocol:
                    name = target_protocol.get('name', 'Unknown')
                    tvl = target_protocol.get('tvl', 0) or 0
                    change_1d = target_protocol.get('change_1d', 0) or 0
                    change_7d = target_protocol.get('change_7d', 0) or 0
                    category = target_protocol.get('category', 'Unknown')
                    chains = target_protocol.get('chains', [])
                    
                    # Format TVL nicely
                    if tvl >= 1_000_000_000:
                        tvl_str = f"${tvl/1_000_000_000:.1f}B"
                    elif tvl >= 1_000_000:
                        tvl_str = f"${tvl/1_000_000:.1f}M"
                    elif tvl >= 1_000:
                        tvl_str = f"${tvl/1_000:.1f}K"
                    else:
                        tvl_str = f"${tvl:.0f}"
                    
                    # Format changes
                    change_1d_str = f"🟢 +{change_1d:.1f}%" if change_1d > 0 else f"🔴 {change_1d:.1f}%" if change_1d < 0 else f"⚪ {change_1d:.1f}%"
                    change_7d_str = f"🟢 +{change_7d:.1f}%" if change_7d > 0 else f"🔴 {change_7d:.1f}%" if change_7d < 0 else f"⚪ {change_7d:.1f}%"
                    
                    result = f"📊 **{name} Protocol Details**\n\n"
                    result += f"💰 **TVL**: {tvl_str}\n"
                    result += f"📈 **24h Change**: {change_1d_str}\n"
                    result += f"📊 **7d Change**: {change_7d_str}\n"
                    result += f"🏷️ **Category**: {category}\n"
                    if chains:
                        result += f"⛓️ **Chains**: {', '.join(chains[:5])}\n"
                    
                    return result
                else:
                    return f"❌ Protocol '{protocol_name or slug}' not found."
            
            # Show top 10 protocols by TVL (default behavior)
            sorted_protocols = sorted(data, key=lambda x: x.get('tvl', 0) or 0, reverse=True)[:10]
            result = "📊 **Top DeFi Protocols by TVL:**\n\n"
            for i, protocol in enumerate(sorted_protocols, 1):
                tvl = protocol.get('tvl', 0) or 0
                name = protocol.get('name', 'Unknown')
                change = protocol.get('change_1d', 0) or 0
                
                # Format TVL nicely
                if tvl >= 1_000_000_000:
                    tvl_str = f"${tvl/1_000_000_000:.1f}B"
                elif tvl >= 1_000_000:
                    tvl_str = f"${tvl/1_000_000:.1f}M"
                elif tvl >= 1_000:
                    tvl_str = f"${tvl/1_000:.1f}K"
                else:
                    tvl_str = f"${tvl:.0f}"
                
                # Format change with emoji
                if change > 0:
                    change_str = f"🟢 +{change:.1f}%"
                elif change < 0:
                    change_str = f"🔴 {change:.1f}%"
                else:
                    change_str = f"⚪ {change:.1f}%"
                
                result += f"{i}. **{name}**\n   💰 {tvl_str} {change_str}\n\n"
            return result
            
        elif data_type == 'chains':
            if not data:
                return "No chains found."
            
            # Show top 10 chains by TVL
            sorted_chains = sorted(data, key=lambda x: x.get('tvl', 0) or 0, reverse=True)[:10]
            result = "⛓️ **Top Blockchains by TVL:**\n\n"
            for i, chain in enumerate(sorted_chains, 1):
                tvl = chain.get('tvl', 0) or 0
                name = chain.get('name', 'Unknown')
                
                # Format TVL nicely
                if tvl >= 1_000_000_000:
                    tvl_str = f"${tvl/1_000_000_000:.1f}B"
                elif tvl >= 1_000_000:
                    tvl_str = f"${tvl/1_000_000:.1f}M"
                elif tvl >= 1_000:
                    tvl_str = f"${tvl/1_000:.1f}K"
                else:
                    tvl_str = f"${tvl:.0f}"
                
                result += f"{i}. **{name}**\n   💰 {tvl_str}\n\n"
            return result
            
        elif data_type == 'yields':
            if not data or not isinstance(data, dict) or 'data' not in data:
                # Handle direct array response
                if isinstance(data, list):
                    pools = data[:10]
                else:
                    return "No yield data found."
            else:
                pools = data['data'][:10]
            
            result = "💰 **Top Yield Opportunities:**\n\n"
            for i, pool in enumerate(pools[:8], 1):  # Show top 8
                project = pool.get('project', 'Unknown')
                symbol = pool.get('symbol', 'Unknown')
                apy = pool.get('apy', 0) or pool.get('apyBase', 0) or 0
                tvl = pool.get('tvlUsd', 0) or 0
                
                # Format TVL nicely
                if tvl >= 1_000_000:
                    tvl_str = f"${tvl/1_000_000:.1f}M"
                elif tvl >= 1_000:
                    tvl_str = f"${tvl/1_000:.1f}K"
                else:
                    tvl_str = f"${tvl:.0f}"
                
                # Format APY with emoji
                if apy > 20:
                    apy_emoji = "🔥"
                elif apy > 10:
                    apy_emoji = "🚀"
                elif apy > 5:
                    apy_emoji = "📈"
                else:
                    apy_emoji = "💰"
                
                result += f"{i}. **{project}** ({symbol})\n   {apy_emoji} {apy:.1f}% APY • 💰 {tvl_str} TVL\n\n"
            return result
            
        elif data_type == 'stablecoins':
            # Handle different response formats
            stablecoins_data = []
            if isinstance(data, dict) and 'peggedAssets' in data:
                stablecoins_data = data['peggedAssets']
            elif isinstance(data, list):
                stablecoins_data = data
            else:
                return "No stablecoin data found."
            
            # Show top 10 stablecoins by market cap
            try:
                stablecoins = sorted(stablecoins_data, 
                                   key=lambda x: x.get('circulating', {}).get('peggedUSD', 0) if isinstance(x.get('circulating'), dict) else x.get('mcap', 0), 
                                   reverse=True)[:10]
            except (TypeError, KeyError):
                stablecoins = stablecoins_data[:10]
            
            result = "🪙 **Top Stablecoins by Market Cap:**\n\n"
            for i, coin in enumerate(stablecoins, 1):
                name = coin.get('name', 'Unknown')
                symbol = coin.get('symbol', 'Unknown')
                mcap = 0
                if isinstance(coin.get('circulating'), dict):
                    mcap = coin.get('circulating', {}).get('peggedUSD', 0)
                else:
                    mcap = coin.get('mcap', 0) or coin.get('circulating', 0)
                result += f"{i}. **{name}** ({symbol}): ${mcap:,.0f}\n"
            return result
            
        elif data_type == 'bridges':
            # Handle different response formats
            bridges_data = []
            if isinstance(data, dict) and 'bridges' in data:
                bridges_data = data['bridges']
            elif isinstance(data, list):
                bridges_data = data
            else:
                return "No bridge data found."
            
            # Show top 10 bridges by volume
            try:
                bridges = sorted(bridges_data, 
                               key=lambda x: x.get('volumePrevDay', 0) or x.get('volume24h', 0), 
                               reverse=True)[:10]
            except (TypeError, KeyError):
                bridges = bridges_data[:10]
            
            result = "🌉 **Top Bridges by 24h Volume:**\n\n"
            for i, bridge in enumerate(bridges, 1):
                name = bridge.get('displayName', bridge.get('name', 'Unknown'))
                volume = bridge.get('volumePrevDay', 0) or bridge.get('volume24h', 0)
                result += f"{i}. **{name}**: ${volume:,.0f}\n"
            return result
            
        else:
            # Generic response for other data types
            return f"📊 **{data_type.title()} Data:**\n\n{str(data)[:500]}..."
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return f"❌ Data not found for '{slug}'"
        return f"❌ HTTP error: {e}"
    except Exception as e:
        logger.error(f"DeFiLlama lookup failed for '{data_type}': {e}")
        return "❌ An unexpected error occurred."

def get_arkham_data(query: str) -> str:
    """Get data from Arkham Intelligence API"""
    api_key = config.get('CRYPTO_API_KEYS', {}).get('arkham')
    if not api_key:
        return "❌ Arkham API key is not configured."
    
    try:
        # Mock response for now - replace with actual Arkham API call
        return f"🔍 **Arkham Intelligence Data for '{query}':**\n\nAPI integration in progress. Please configure your Arkham API key."
    except Exception as e:
        logger.error(f"Arkham API error: {e}")
        return "❌ Error fetching Arkham data."

def get_nansen_data(address: str) -> str:
    """Get wallet labels from Nansen API"""
    api_key = config.get('CRYPTO_API_KEYS', {}).get('nansen')
    if not api_key:
        return "❌ Nansen API key is not configured."
    
    try:
        # Mock response for now - replace with actual Nansen API call
        return f"🏷️ **Nansen Labels for {address}:**\n\nAPI integration in progress. Please configure your Nansen API key."
    except Exception as e:
        logger.error(f"Nansen API error: {e}")
        return "❌ Error fetching Nansen data."

def create_arkham_alert(address: str, amount: str, user_id: int, chat_id: int) -> str:
    """Create an alert for large transactions"""
    try:
        # Mock alert creation - replace with actual implementation
        return f"🔔 **Alert Created**\n\nWatching address `{address}` for transactions > ${amount}\n\nYou'll be notified when this occurs."
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        return "❌ Error creating alert."

def query_defillama(data_type: str, slug: str = None) -> str:
    base_url = "https://api.llama.fi"
    
    # Enhanced endpoints with more DeFiLlama API features
    endpoints = {
        'tvl': f"/tvl/{slug}" if slug else "/charts",
        'revenue': f"/summary/fees/{slug}?dataType=dailyRevenue" if slug else "/overview/fees",
        'raises': f"/raises?protocol={slug}" if slug else "/raises",
        'protocols': "/protocols",
        'chains': "/chains",
        'yields': "/pools",
        'stablecoins': "/stablecoins",
        'volumes': "/overview/dexs",
        'bridges': "/bridges",
        'liquidations': "/liquidations/protocols",
        'treasury': "/treasury",
        'governance': "/governance/snapshot",
        'nfts': "/nfts/collections",
        'options': "/overview/options",
        'derivatives': "/overview/derivatives"
    }
    
    if data_type not in endpoints:
        available_types = ', '.join(endpoints.keys())
        return f"❌ Invalid type '{data_type}'. Available types: {available_types}"
    
    try:
        url = base_url + endpoints[data_type]
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Format response based on data type
        if data_type == 'tvl':
            if slug:
                return f"📈 **{slug.title()}** TVL: `${data:,.2f}`" if isinstance(data, (int, float)) else "Unexpected TVL data."
            else:
                total_tvl = sum([chain.get('tvl', 0) for chain in data])
                return f"📊 **Total DeFi TVL**: `${total_tvl:,.2f}`\n\n**Top Chains:**\n" + "\n".join([f"• {chain['name']}: ${chain.get('tvl', 0):,.0f}" for chain in data[:10]])
        
        elif data_type == 'revenue':
            if slug:
                return f"💰 **{slug.title()}** 24h Revenue: `${(data.get('total24h', 0) or 0):,.2f}`"
            else:
                total_24h = data.get('total24h', 0)
                return f"💰 **Total DeFi 24h Fees**: `${total_24h:,.2f}`"
        
        elif data_type == 'protocols':
            # Handle both list and dict responses
            if isinstance(data, list):
                protocols_list = data
            elif isinstance(data, dict) and 'protocols' in data:
                protocols_list = data['protocols']
            else:
                protocols_list = data if data else []
            
            # Filter and sort protocols with valid TVL
            valid_protocols = [p for p in protocols_list if isinstance(p.get('tvl'), (int, float)) and p.get('tvl', 0) > 0]
            top_protocols = sorted(valid_protocols, key=lambda x: x.get('tvl', 0), reverse=True)[:10]
            
            result = "🏆 **Top DeFi Protocols by TVL:**\n\n"
            for i, protocol in enumerate(top_protocols, 1):
                tvl = protocol.get('tvl', 0)
                name = protocol.get('name', 'Unknown')
                result += f"{i}. **{name}**: ${tvl:,.0f}\n"
            return result
        
        elif data_type == 'chains':
            result = "⛓️ **Blockchain TVL Rankings:**\n\n"
            for i, chain in enumerate(data[:15], 1):
                result += f"{i}. **{chain['name']}**: ${chain.get('tvl', 0):,.0f}\n"
            return result
        
        elif data_type == 'yields':
            if isinstance(data, dict) and 'data' in data:
                pools = data['data'][:10]
            else:
                pools = data[:10] if isinstance(data, list) else []
            
            result = "🌾 **Top Yield Farming Pools:**\n\n"
            for pool in pools:
                apy = pool.get('apy', 0)
                tvl = pool.get('tvlUsd', 0)
                project = pool.get('project', 'Unknown')
                symbol = pool.get('symbol', 'Unknown')
                result += f"• **{project}** ({symbol}): {apy:.2f}% APY | TVL: ${tvl:,.0f}\n"
            return result
        
        elif data_type == 'stablecoins':
            result = "💵 **Stablecoin Market:**\n\n"
            for coin in data[:10]:
                mcap = coin.get('circulating', {}).get('peggedUSD', 0)
                result += f"• **{coin.get('name', 'Unknown')}**: ${mcap:,.0f}\n"
            return result
        
        elif data_type == 'volumes':
            total_volume = data.get('total24h', 0)
            result = f"📊 **DEX Volume (24h)**: `${total_volume:,.0f}`\n\n**Top DEXs:**\n"
            protocols = data.get('protocols', [])[:10]
            for protocol in protocols:
                volume = protocol.get('total24h', 0)
                result += f"• **{protocol.get('name', 'Unknown')}**: ${volume:,.0f}\n"
            return result
        
        elif data_type == 'bridges':
            result = "🌉 **Cross-Chain Bridges:**\n\n"
            for bridge in data[:10]:
                volume = bridge.get('volumePrevDay', 0)
                result += f"• **{bridge.get('name', 'Unknown')}**: ${volume:,.0f} (24h)\n"
            return result
        
        elif data_type == 'raises':
            if slug and not data.get('raises'):
                return f"No funding rounds found for **{slug.title()}**."
            
            raises = data.get('raises', data) if isinstance(data, dict) else data
            if not raises:
                return "No recent funding rounds found."
            
            result = f"💸 **Recent Funding Rounds:**\n\n"
            for r in raises[:10]:
                amount = r.get('amount', 0)
                date = r.get('date', 'Unknown')
                name = r.get('name', slug.title() if slug else 'Unknown')
                investors = r.get('leadInvestors', [])
                investor_text = investors[0] if investors else 'undisclosed'
                result += f"• **{name}** ({date}): ${amount:,} from {investor_text}\n"
            return result
        
        else:
            # Generic response for other endpoints
            if isinstance(data, dict):
                if 'total24h' in data:
                    return f"📊 **{data_type.title()} 24h**: `${data['total24h']:,.2f}`"
                elif 'totalVolume' in data:
                    return f"📊 **{data_type.title()} Volume**: `${data['totalVolume']:,.2f}`"
            
            return f"📊 **{data_type.title()} Data**: Retrieved successfully (complex data structure)"
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return f"❌ Data not found for '{slug}'" if slug else f"❌ Endpoint '{data_type}' not found"
        return f"❌ HTTP error: {e}"
    except Exception as e:
        logger.error(f"DeFiLlama lookup failed for '{data_type}' (slug: {slug}): {e}")
        return f"❌ An unexpected error occurred: {str(e)[:100]}..."

def get_arkham_data(query: str) -> str:
    api_key = config.get('CRYPTO_API_KEYS').get('arkham')
    if not api_key: return "Error: Arkham API key is not configured."
    try:
        headers = {"API-Key": api_key}; params = {"name": query}
        response = requests.get("https://api.arkhamintelligence.com/v1/search", headers=headers, params=params, timeout=10)
        response.raise_for_status(); data = response.json()
        if not data.get('entities'): return f"No entities found for '{query}' on Arkham."
        entity = data['entities'][0]
        return (f"**Arkham Entity Found:** `{entity['name']}`\n"
                f"**Type:** `{entity['type']}`\n"
                f"**Address:** `{entity.get('address', 'N/A')}`")
    except Exception as e: logger.error(f"Arkham API call failed for '{query}': {e}"); return f"An error occurred during the Arkham API call: {e}"

def get_nansen_data(query: str) -> str:
    api_key = config.get('CRYPTO_API_KEYS').get('nansen')
    if not api_key: return "Error: Nansen API key is not configured."
    try:
        headers = {"accept": "application/json", "API-KEY": api_key}
        response = requests.get(f"https://api.nansen.ai/v1/wallet-labels/{query}", headers=headers, timeout=10)
        response.raise_for_status(); data = response.json()
        if not data.get('result'): return f"No labels found for address `{query}` on Nansen."
        labels = [item['label'] for item in data['result']]
        return f"**Nansen Labels for `{query}`:**\n- " + "\n- ".join(labels)
    except requests.exceptions.HTTPError as e: return f"Could not get Nansen data. Status: {e.response.status_code}"
    except Exception as e: logger.error(f"Nansen API call failed for '{query}': {e}"); return f"An error occurred during the Nansen API call: {e}"

def create_arkham_alert(user_id: int, address: str, amount_usd: float) -> dict:
    api_key = config.get('CRYPTO_API_KEYS').get('arkham'); webhook_url = config.get('ARKHAM_WEBHOOK_URL')
    if not api_key: return {"success": False, "message": "Error: Arkham API key is not configured."}
    if not webhook_url: return {"success": False, "message": "Error: The bot's webhook URL is not configured."}
    payload = {
        "name": f"TG-Bot Alert for User {user_id} on {address[:8]}", "alertType": "ADDRESS_ACTIVITY",
        "channel": "WEBHOOK", "channelAddress": webhook_url, "address": address, "threshold": str(amount_usd)
    }
    headers = {"API-Key": api_key}
    try:
        response = requests.post("https://api.arkhamintelligence.com/v1/c/alerter/create", headers=headers, json=payload, timeout=15)
        response.raise_for_status(); data = response.json()
        if data.get('id'): return {"success": True, "alert_id": data['id'], "message": f"Successfully created alert for `{address}`."}
        else: return {"success": False, "message": f"Arkham API returned success but no alert ID. Response: {data}"}
    except requests.exceptions.HTTPError as e:
        error_details = e.response.json().get('error', e.response.text)
        logger.error(f"Arkham alert creation failed: {error_details}"); return {"success": False, "message": f"Arkham API Error: {error_details}"}
    except Exception as e: logger.error(f"Unexpected error creating Arkham alert: {e}"); return {"success": False, "message": "An unexpected error occurred."}

async def get_protocol_tvl(protocol_name: str) -> dict:
    """Get TVL for a specific protocol"""
    try:
        protocol = search_protocol_by_name(protocol_name)
        if protocol:
            return {
                "success": True,
                "protocol": protocol.get('name', 'Unknown'),
                "tvl": protocol.get('tvl', 0),
                "change_1d": protocol.get('change_1d', 0),
                "change_7d": protocol.get('change_7d', 0),
                "category": protocol.get('category', 'Unknown')
            }
        else:
            return {
                "success": False,
                "error": f"Protocol '{protocol_name}' not found",
                "message": f"Could not find protocol '{protocol_name}'"
            }
    except Exception as e:
        logger.error(f"Error getting TVL for protocol '{protocol_name}': {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Error retrieving TVL for '{protocol_name}'"
        }

async def get_price_data(symbol: str) -> dict:
    """Get price data for a cryptocurrency symbol"""
    try:
        # Use CoinGecko API for price data
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': symbol.lower(),
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_market_cap': 'true'
        }
        
        # Try with symbol first
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                coin_id = list(data.keys())[0]
                coin_data = data[coin_id]
                return {
                    "success": True,
                    "symbol": symbol.upper(),
                    "price": coin_data.get('usd', 0),
                    "change_24h": coin_data.get('usd_24h_change', 0),
                    "market_cap": coin_data.get('usd_market_cap', 0)
                }
        
        # If direct symbol lookup fails, try searching by symbol
        search_url = f"https://api.coingecko.com/api/v3/search"
        search_params = {'query': symbol}
        search_response = requests.get(search_url, params=search_params, timeout=10)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            coins = search_data.get('coins', [])
            
            if coins:
                # Use the first match
                coin_id = coins[0]['id']
                params['ids'] = coin_id
                
                price_response = requests.get(url, params=params, timeout=10)
                if price_response.status_code == 200:
                    price_data = price_response.json()
                    if price_data and coin_id in price_data:
                        coin_data = price_data[coin_id]
                        return {
                            "success": True,
                            "symbol": symbol.upper(),
                            "name": coins[0].get('name', symbol),
                            "price": coin_data.get('usd', 0),
                            "change_24h": coin_data.get('usd_24h_change', 0),
                            "market_cap": coin_data.get('usd_market_cap', 0)
                        }
        
        return {
            "success": False,
            "error": "Symbol not found",
            "message": f"Could not find price data for '{symbol}'"
        }
        
    except Exception as e:
        logger.error(f"Error getting price data for '{symbol}': {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Error retrieving price for '{symbol}'"
        }
