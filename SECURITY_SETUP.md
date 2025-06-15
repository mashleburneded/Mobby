# Möbius AI Assistant - Security Setup Guide

## 🔐 **Encryption Key Generation**

The `BOT_MASTER_ENCRYPTION_KEY` is a critical security component that encrypts all sensitive data stored by the bot. This guide shows you how to generate it securely.

## 🚨 **CRITICAL SECURITY WARNING**

⚠️ **The encryption key is the master key for all your bot's encrypted data. If you lose it, ALL encrypted data becomes permanently unrecoverable.**

- **NEVER** commit this key to version control
- **ALWAYS** store it securely (password manager, secure vault)
- **BACKUP** the key in multiple secure locations
- **ROTATE** the key periodically for maximum security

## 🔑 **Method 1: Python Command (Recommended)**

### **Quick Generation**
```bash
python -c "from cryptography.fernet import Fernet; print('BOT_MASTER_ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
```

### **Step-by-Step Generation**
```bash
# 1. Ensure cryptography is installed
pip install cryptography

# 2. Generate the key
python3 << EOF
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print("=" * 60)
print("🔐 MÖBIUS AI ASSISTANT ENCRYPTION KEY")
print("=" * 60)
print(f"BOT_MASTER_ENCRYPTION_KEY={key.decode()}")
print("=" * 60)
print("⚠️  CRITICAL: Save this key securely!")
print("⚠️  If lost, all encrypted data is unrecoverable!")
print("=" * 60)
EOF
```

## 🔑 **Method 2: OpenSSL (Alternative)**

If you prefer using OpenSSL:

```bash
# Generate 32 random bytes and base64 encode
openssl rand -base64 32
```

**Note:** You'll need to format this for Fernet compatibility:
```bash
python3 << EOF
import base64
from cryptography.fernet import Fernet

# Replace 'YOUR_OPENSSL_OUTPUT' with the actual output from openssl
openssl_key = "YOUR_OPENSSL_OUTPUT"
try:
    # Ensure it's 32 bytes when decoded
    key_bytes = base64.urlsafe_b64decode(openssl_key + '==')[:32]
    # Re-encode for Fernet
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    print(f"BOT_MASTER_ENCRYPTION_KEY={fernet_key.decode()}")
except:
    print("❌ Invalid key format. Use Method 1 instead.")
EOF
```

## 🔑 **Method 3: Secure Random (Advanced)**

For maximum entropy:

```bash
python3 << EOF
import secrets
import base64
from cryptography.fernet import Fernet

# Generate 32 cryptographically secure random bytes
key_bytes = secrets.token_bytes(32)
# Encode for Fernet
fernet_key = base64.urlsafe_b64encode(key_bytes)
print(f"BOT_MASTER_ENCRYPTION_KEY={fernet_key.decode()}")

# Verify the key works
try:
    f = Fernet(fernet_key)
    test = f.encrypt(b"test")
    f.decrypt(test)
    print("✅ Key validation successful!")
except:
    print("❌ Key validation failed!")
EOF
```

## 📝 **Setting Up Your .env File**

1. **Copy the example file:**
```bash
cp .env.example .env
```

2. **Edit the .env file:**
```bash
nano .env  # or your preferred editor
```

3. **Add your generated key:**
```env
# Core Security Configuration
BOT_MASTER_ENCRYPTION_KEY=your_generated_key_here

# Required Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_CHAT_ID=your_target_chat_id

# AI Provider Keys (at least one required)
GROQ_API_KEY=your_groq_key_here
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Optional Service Keys
ARKHAM_API_KEY=your_arkham_key_here
NANSEN_API_KEY=your_nansen_key_here
WHOP_BEARER_TOKEN=your_whop_token_here
ETHEREUM_RPC_URL=your_rpc_url_here
```

## 🔒 **Key Security Best Practices**

### **Storage Security**
- **Password Manager:** Store in 1Password, Bitwarden, or similar
- **Secure Notes:** Use encrypted note-taking apps
- **Hardware Security:** Consider hardware security modules (HSM) for production
- **Air-Gapped Backup:** Store offline copies in secure locations

### **Access Control**
- **Principle of Least Privilege:** Only authorized personnel should have access
- **Audit Trail:** Log all access to the encryption key
- **Regular Rotation:** Change the key periodically (requires data migration)
- **Emergency Procedures:** Have a plan for key compromise scenarios

### **Environment Security**
```bash
# Set restrictive permissions on .env file
chmod 600 .env

# Verify permissions
ls -la .env
# Should show: -rw------- (owner read/write only)

# For production, consider using environment variables instead of .env files
export BOT_MASTER_ENCRYPTION_KEY="your_key_here"
```

## 🔄 **Key Rotation (Advanced)**

If you need to rotate your encryption key:

### **1. Generate New Key**
```bash
python -c "from cryptography.fernet import Fernet; print('NEW_KEY=' + Fernet.generate_key().decode())"
```

### **2. Migration Script**
```python
# key_rotation.py
import sqlite3
from cryptography.fernet import Fernet

# Your keys
OLD_KEY = "your_old_key_here"
NEW_KEY = "your_new_key_here"

old_fernet = Fernet(OLD_KEY.encode())
new_fernet = Fernet(NEW_KEY.encode())

# Connect to database
conn = sqlite3.connect('data/user_data.sqlite')
cursor = conn.cursor()

# Get all encrypted data
cursor.execute("SELECT user_id, key, value FROM user_properties WHERE key LIKE '%encrypted%'")
encrypted_data = cursor.fetchall()

# Re-encrypt with new key
for user_id, key, encrypted_value in encrypted_data:
    try:
        # Decrypt with old key
        decrypted = old_fernet.decrypt(encrypted_value.encode())
        # Encrypt with new key
        new_encrypted = new_fernet.encrypt(decrypted).decode()
        # Update database
        cursor.execute("UPDATE user_properties SET value = ? WHERE user_id = ? AND key = ?", 
                      (new_encrypted, user_id, key))
        print(f"✅ Rotated key for user {user_id}, property {key}")
    except Exception as e:
        print(f"❌ Failed to rotate key for user {user_id}, property {key}: {e}")

conn.commit()
conn.close()
print("🔄 Key rotation complete!")
```

### **3. Update Environment**
```bash
# Update .env with new key
sed -i 's/BOT_MASTER_ENCRYPTION_KEY=.*/BOT_MASTER_ENCRYPTION_KEY=your_new_key_here/' .env

# Restart the bot
systemctl restart mobius  # or your restart method
```

## ✅ **Verification**

Test your encryption setup:

```bash
python3 << EOF
import sys
sys.path.append('src')

try:
    from config import config
    key = config.get('BOT_MASTER_ENCRYPTION_KEY')
    
    if not key:
        print("❌ BOT_MASTER_ENCRYPTION_KEY not found in configuration")
        exit(1)
    
    from cryptography.fernet import Fernet
    fernet = Fernet(key.encode())
    
    # Test encryption/decryption
    test_data = b"Möbius AI Assistant Test"
    encrypted = fernet.encrypt(test_data)
    decrypted = fernet.decrypt(encrypted)
    
    if decrypted == test_data:
        print("✅ Encryption key is valid and working!")
        print(f"✅ Key length: {len(key)} characters")
        print("✅ Ready for secure operations")
    else:
        print("❌ Encryption test failed")
        
except Exception as e:
    print(f"❌ Encryption setup error: {e}")
    print("💡 Make sure you've set BOT_MASTER_ENCRYPTION_KEY in your .env file")
EOF
```

## 🚨 **Emergency Procedures**

### **Key Compromise**
If you suspect your encryption key has been compromised:

1. **Immediate Actions:**
   - Stop the bot immediately
   - Generate a new encryption key
   - Rotate all API keys and tokens
   - Review audit logs for suspicious activity

2. **Data Recovery:**
   - Use the key rotation script above
   - Verify all encrypted data integrity
   - Update all environment configurations

3. **Security Review:**
   - Audit all access logs
   - Review security procedures
   - Implement additional security measures

### **Key Loss**
If you lose your encryption key:

⚠️ **WARNING: All encrypted data will be permanently lost**

1. **Accept Data Loss:**
   - Encrypted user data cannot be recovered
   - API keys and sensitive settings will be lost
   - Users will need to re-enter sensitive information

2. **Clean Restart:**
   - Generate new encryption key
   - Clear encrypted database entries
   - Notify users of the data loss
   - Implement better backup procedures

## 📞 **Support**

For security-related issues:
- Review this guide thoroughly
- Check the troubleshooting section in DEPLOYMENT_ENHANCED.md
- Ensure all security best practices are followed
- Never share encryption keys in support requests

Remember: **Security is non-negotiable** for the Möbius AI Assistant. Take time to properly secure your encryption keys!