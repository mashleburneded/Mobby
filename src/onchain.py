# src/onchain.py
"""
Enhanced On-Chain Wallet Management for Möbius AI Assistant
Provides secure wallet creation, balance checking, sending, and swapping functionality
"""

import os
import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from web3 import Web3
from eth_account import Account
from cryptography.fernet import Fernet
from config import config
from user_db import get_user_property, set_user_property

logger = logging.getLogger(__name__)

class WalletManager:
    """Enhanced wallet management with full functionality"""
    
    def __init__(self):
        self.supported_networks = {
            "ethereum": {
                "rpc_url": config.get("ETHEREUM_RPC_URL", "https://eth.llamarpc.com"),
                "chain_id": 1,
                "native_symbol": "ETH",
                "explorer": "https://etherscan.io"
            },
            "polygon": {
                "rpc_url": config.get("POLYGON_RPC_URL", "https://polygon.llamarpc.com"),
                "chain_id": 137,
                "native_symbol": "MATIC",
                "explorer": "https://polygonscan.com"
            },
            "bsc": {
                "rpc_url": config.get("BSC_RPC_URL", "https://bsc.llamarpc.com"),
                "chain_id": 56,
                "native_symbol": "BNB",
                "explorer": "https://bscscan.com"
            }
        }
        
        # Common ERC-20 tokens
        self.common_tokens = {
            "ethereum": {
                "USDC": "0xA0b86a33E6441b8e776f89d2b5B977c737C8e8e8",
                "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                "UNI": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
            },
            "polygon": {
                "USDC": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
                "USDT": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
                "WMATIC": "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"
            }
        }
    
    def create_wallet(self) -> Dict[str, str]:
        """Creates a new Ethereum-compatible wallet"""
        try:
            Account.enable_unaudited_hdwallet_features()
            account, mnemonic = Account.create_with_mnemonic()
            
            return {
                "address": account.address,
                "private_key": account.key.hex(),
                "mnemonic": mnemonic,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error creating wallet: {e}")
            return {
                "status": "error",
                "message": f"Failed to create wallet: {str(e)}"
            }
    
    def encrypt_private_key(self, private_key: str, password: str) -> bytes:
        """Encrypts a private key with a user-provided password"""
        try:
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            from base64 import urlsafe_b64encode

            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
            )
            key = urlsafe_b64encode(kdf.derive(password.encode()))
            f = Fernet(key)
            encrypted_pk = f.encrypt(private_key.encode())
            return salt + encrypted_pk
        except Exception as e:
            logger.error(f"Error encrypting private key: {e}")
            raise

    def decrypt_private_key(self, encrypted_data: bytes, password: str) -> str:
        """Decrypts a private key with the user's password"""
        try:
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            from base64 import urlsafe_b64encode
            
            salt = encrypted_data[:16]
            encrypted_pk = encrypted_data[16:]
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
            )
            key = urlsafe_b64encode(kdf.derive(password.encode()))
            f = Fernet(key)
            decrypted_pk = f.decrypt(encrypted_pk)
            return decrypted_pk.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt private key: {e}")
            raise ValueError(f"Failed to decrypt private key: {e}")

    async def get_wallet_balance(self, address: str, network: str = "ethereum") -> Dict[str, Any]:
        """Gets comprehensive wallet balance information"""
        try:
            if network not in self.supported_networks:
                return {"error": f"Unsupported network: {network}"}
            
            network_config = self.supported_networks[network]
            w3 = Web3(Web3.HTTPProvider(network_config["rpc_url"]))
            
            if not w3.is_connected():
                return {"error": f"Could not connect to {network} RPC"}
            
            # Get native token balance
            balance_wei = w3.eth.get_balance(w3.to_checksum_address(address))
            balance_native = w3.from_wei(balance_wei, 'ether')
            
            # Get token balances
            token_balances = await self._get_token_balances(w3, address, network)
            
            # Get USD values (simplified - in production use price APIs)
            usd_values = await self._get_usd_values(network, balance_native, token_balances)
            
            return {
                "address": address,
                "network": network,
                "native_balance": {
                    "symbol": network_config["native_symbol"],
                    "balance": float(balance_native),
                    "usd_value": usd_values.get("native", 0)
                },
                "token_balances": token_balances,
                "total_usd_value": sum(usd_values.values()),
                "explorer_url": f"{network_config['explorer']}/address/{address}"
            }
            
        except Exception as e:
            logger.error(f"Error getting wallet balance: {e}")
            return {"error": str(e)}
    
    async def _get_token_balances(self, w3: Web3, address: str, network: str) -> List[Dict[str, Any]]:
        """Get ERC-20 token balances"""
        token_balances = []
        
        try:
            # ERC-20 ABI for balanceOf function
            erc20_abi = [
                {
                    "constant": True,
                    "inputs": [{"name": "_owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "balance", "type": "uint256"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "decimals",
                    "outputs": [{"name": "", "type": "uint8"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "symbol",
                    "outputs": [{"name": "", "type": "string"}],
                    "type": "function"
                }
            ]
            
            if network in self.common_tokens:
                for symbol, contract_address in self.common_tokens[network].items():
                    try:
                        contract = w3.eth.contract(
                            address=w3.to_checksum_address(contract_address),
                            abi=erc20_abi
                        )
                        
                        balance = contract.functions.balanceOf(w3.to_checksum_address(address)).call()
                        decimals = contract.functions.decimals().call()
                        
                        if balance > 0:
                            balance_formatted = balance / (10 ** decimals)
                            token_balances.append({
                                "symbol": symbol,
                                "balance": balance_formatted,
                                "contract_address": contract_address,
                                "decimals": decimals
                            })
                    except Exception as e:
                        logger.warning(f"Error getting balance for {symbol}: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Error getting token balances: {e}")
        
        return token_balances
    
    async def _get_usd_values(self, network: str, native_balance: float, token_balances: List[Dict]) -> Dict[str, float]:
        """Get USD values for tokens (simplified implementation)"""
        usd_values = {}
        
        try:
            # Simplified price mapping - in production, use real price APIs
            price_map = {
                "ethereum": {"ETH": 2000},
                "polygon": {"MATIC": 0.8},
                "bsc": {"BNB": 300}
            }
            
            # Native token USD value
            if network in price_map:
                native_symbol = self.supported_networks[network]["native_symbol"]
                native_price = price_map[network].get(native_symbol, 0)
                usd_values["native"] = float(native_balance) * native_price
            
            # Token USD values (simplified)
            token_prices = {"USDC": 1.0, "USDT": 1.0, "UNI": 8.0, "WETH": 2000}
            
            for token in token_balances:
                symbol = token["symbol"]
                balance = token["balance"]
                price = token_prices.get(symbol, 0)
                usd_values[symbol] = balance * price
        
        except Exception as e:
            logger.error(f"Error calculating USD values: {e}")
        
        return usd_values
    
    async def send_transaction(
        self, 
        from_address: str, 
        to_address: str, 
        amount: float, 
        private_key: str,
        network: str = "ethereum",
        token_contract: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send native tokens or ERC-20 tokens"""
        try:
            if network not in self.supported_networks:
                return {"error": f"Unsupported network: {network}"}
            
            network_config = self.supported_networks[network]
            w3 = Web3(Web3.HTTPProvider(network_config["rpc_url"]))
            
            if not w3.is_connected():
                return {"error": f"Could not connect to {network} RPC"}
            
            # Get account from private key
            account = Account.from_key(private_key)
            
            if account.address.lower() != from_address.lower():
                return {"error": "Private key does not match from address"}
            
            # Get nonce
            nonce = w3.eth.get_transaction_count(w3.to_checksum_address(from_address))
            
            # Get gas price
            gas_price = w3.eth.gas_price
            
            if token_contract:
                # ERC-20 transfer
                tx_hash = await self._send_token_transaction(
                    w3, account, to_address, amount, token_contract, nonce, gas_price
                )
            else:
                # Native token transfer
                tx_hash = await self._send_native_transaction(
                    w3, account, to_address, amount, nonce, gas_price
                )
            
            return {
                "status": "success",
                "transaction_hash": tx_hash,
                "explorer_url": f"{network_config['explorer']}/tx/{tx_hash}"
            }
            
        except Exception as e:
            logger.error(f"Error sending transaction: {e}")
            return {"error": str(e)}
    
    async def _send_native_transaction(
        self, 
        w3: Web3, 
        account: Account, 
        to_address: str, 
        amount: float, 
        nonce: int, 
        gas_price: int
    ) -> str:
        """Send native token transaction"""
        
        # Build transaction
        transaction = {
            'to': w3.to_checksum_address(to_address),
            'value': w3.to_wei(amount, 'ether'),
            'gas': 21000,
            'gasPrice': gas_price,
            'nonce': nonce,
        }
        
        # Sign transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, account.key)
        
        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return tx_hash.hex()
    
    async def _send_token_transaction(
        self, 
        w3: Web3, 
        account: Account, 
        to_address: str, 
        amount: float, 
        token_contract: str, 
        nonce: int, 
        gas_price: int
    ) -> str:
        """Send ERC-20 token transaction"""
        
        # ERC-20 transfer ABI
        erc20_abi = [
            {
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]
        
        # Get contract
        contract = w3.eth.contract(
            address=w3.to_checksum_address(token_contract),
            abi=erc20_abi
        )
        
        # Get token decimals
        decimals = contract.functions.decimals().call()
        
        # Convert amount to token units
        amount_units = int(amount * (10 ** decimals))
        
        # Build transaction
        transaction = contract.functions.transfer(
            w3.to_checksum_address(to_address),
            amount_units
        ).build_transaction({
            'from': account.address,
            'gas': 100000,
            'gasPrice': gas_price,
            'nonce': nonce,
        })
        
        # Sign transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, account.key)
        
        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return tx_hash.hex()
    
    async def swap_tokens(
        self, 
        from_token: str, 
        to_token: str, 
        amount: float, 
        wallet_address: str,
        private_key: str,
        network: str = "ethereum",
        slippage: float = 0.5
    ) -> Dict[str, Any]:
        """Swap tokens using DEX aggregators (simplified implementation)"""
        try:
            # This is a simplified implementation
            # In production, integrate with 1inch, 0x, or other DEX aggregators
            
            return {
                "status": "info",
                "message": "Token swapping feature is under development. Please use external DEX platforms for now.",
                "suggested_platforms": [
                    "Uniswap (https://app.uniswap.org)",
                    "1inch (https://app.1inch.io)",
                    "SushiSwap (https://app.sushi.com)"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error swapping tokens: {e}")
            return {"error": str(e)}
    
    def save_wallet_for_user(self, user_id: int, wallet_data: Dict[str, str], password: str) -> bool:
        """Save encrypted wallet data for user"""
        try:
            # Encrypt private key
            encrypted_pk = self.encrypt_private_key(wallet_data["private_key"], password)
            
            # Store wallet info (without private key)
            wallet_info = {
                "address": wallet_data["address"],
                "encrypted_private_key": encrypted_pk.hex(),
                "mnemonic_encrypted": self.encrypt_private_key(wallet_data["mnemonic"], password).hex()
            }
            
            set_user_property(user_id, "wallet_info", wallet_info)
            return True
            
        except Exception as e:
            logger.error(f"Error saving wallet for user: {e}")
            return False
    
    def get_user_wallet(self, user_id: int) -> Optional[Dict[str, str]]:
        """Get user's wallet information (without private key)"""
        try:
            wallet_info = get_user_property(user_id, "wallet_info")
            if wallet_info and "address" in wallet_info:
                return {
                    "address": wallet_info["address"],
                    "has_private_key": "encrypted_private_key" in wallet_info
                }
            return None
        except Exception as e:
            logger.error(f"Error getting user wallet: {e}")
            return None
    
    def get_supported_networks(self) -> List[str]:
        """Get list of supported networks"""
        return list(self.supported_networks.keys())

# Global instance
wallet_manager = WalletManager()

# Export functions for backward compatibility
def create_wallet() -> Dict[str, str]:
    """Creates a new Ethereum account"""
    return wallet_manager.create_wallet()

def encrypt_private_key(private_key: str, password: str) -> bytes:
    """Encrypts a private key with a user-provided password"""
    return wallet_manager.encrypt_private_key(private_key, password)

def decrypt_private_key(encrypted_data: bytes, password: str) -> Optional[str]:
    """Decrypts a private key with the user's password"""
    return wallet_manager.decrypt_private_key(encrypted_data, password)

async def get_wallet_balance(address: str, network: str = "ethereum") -> Dict[str, Any]:
    """Gets comprehensive wallet balance information"""
    return await wallet_manager.get_wallet_balance(address, network)

async def send_transaction(
    from_address: str, 
    to_address: str, 
    amount: float, 
    private_key: str,
    network: str = "ethereum",
    token_contract: Optional[str] = None
) -> Dict[str, Any]:
    """Send native tokens or ERC-20 tokens"""
    return await wallet_manager.send_transaction(
        from_address, to_address, amount, private_key, network, token_contract
    )