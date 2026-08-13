# 🔐 Wallet Setup Guide — Your Gateway to UBEC Tokens

**A Complete Guide to Creating and Configuring Your Stellar Wallet**

---

## Overview

To participate in the Ubuntu Bioregional Economic Commons, you'll need a Stellar wallet. This guide walks you through creating a wallet, activating it, and setting up trustlines for all four UBEC tokens.

> 💡 **Time Required:** 10-15 minutes  
> **Cost:** ~2 XLM ($0.20-0.50 USD) for wallet activation

---

## What is a Stellar Wallet?

A Stellar wallet is your personal interface to the Stellar blockchain where UBEC tokens live. It allows you to:

- **Receive** UBEC tokens from the community
- **Send** tokens to other participants
- **Hold** your tokens securely
- **View** your transaction history
- **Participate** in the UBEC ecosystem

Your wallet has two keys:
- **Public Key** (starts with "G") — Your address, safe to share
- **Secret Key** (starts with "S") — Your password, NEVER share this

---

## Step 1: Choose Your Wallet

### Recommended Wallets

| Wallet | Best For | Platform | Difficulty |
|--------|----------|----------|------------|
| **[Lobstr](https://lobstr.co/)** | Beginners | Mobile & Web | ⭐ Easy |
| **[Solar Wallet](https://solarwallet.io/)** | General use | Mobile & Desktop | ⭐ Easy |
| **[Freighter](https://freighter.app/)** | Browser integration | Chrome/Firefox Extension | ⭐⭐ Medium |
| **[Albedo](https://albedo.link/)** | Advanced users | Browser-based | ⭐⭐⭐ Advanced |
| **[Stellar Laboratory](https://laboratory.stellar.org/)** | Developers | Web-based | ⭐⭐⭐ Advanced |

### Our Recommendations

**For Most Users:** Start with **Lobstr** or **Solar Wallet**
- User-friendly interface
- Built-in asset discovery
- Easy trustline management
- Available on mobile and desktop

**For Developers:** Use **Freighter** or **Stellar Laboratory**
- Browser extension integration
- Direct blockchain interaction
- Advanced transaction options
- API and SDK compatibility

---

## Step 2: Create Your Wallet

### Option A: Lobstr (Recommended for Beginners)

1. **Download the App**
   - iOS: [App Store](https://apps.apple.com/app/lobstr-stellar-wallet/id1404357892)
   - Android: [Google Play](https://play.google.com/store/apps/details?id=com.lobstr.client)
   - Web: [lobstr.co](https://lobstr.co/)

2. **Create Account**
   - Open Lobstr and tap "Create Account"
   - Enter your email address
   - Create a strong password
   - Verify your email

3. **Secure Your Recovery Phrase**
   - Lobstr will display a 24-word recovery phrase
   - **Write it down on paper** — not digitally!
   - Store in a safe, secure location
   - This phrase can restore your wallet if you lose access

4. **Note Your Public Key**
   - Find your public key in the app (starts with "G")
   - This is the address you'll share to receive tokens

### Option B: Solar Wallet

1. **Download Solar Wallet**
   - Desktop: [solarwallet.io](https://solarwallet.io/)
   - Mobile: Available on iOS and Android

2. **Create New Wallet**
   - Click "Create New Wallet"
   - Choose a strong password

3. **Backup Your Secret Key**
   - Solar will display your secret key (starts with "S")
   - **Write it down on paper immediately**
   - Store securely — this is your only backup!

4. **Record Your Public Key**
   - Your public key (starts with "G") is your wallet address

### Option C: Freighter (For Browser Integration)

1. **Install the Extension**
   - Chrome: [Chrome Web Store](https://chrome.google.com/webstore/detail/freighter/bcacfldlkkdogcmkkibnjlakofdplcbk)
   - Firefox: [Firefox Add-ons](https://addons.mozilla.org/en-US/firefox/addon/freighter/)

2. **Create New Wallet**
   - Click the Freighter icon in your browser
   - Select "Create New Wallet"
   - Set a strong password

3. **Backup Your Recovery Phrase**
   - Write down the 24-word phrase
   - Store securely offline

4. **Access Your Keys**
   - Click "Show Backup Phrase" in settings to review
   - Your public key is displayed on the main screen

---

## Step 3: Activate Your Wallet

New Stellar wallets require a minimum balance of **1 XLM** to activate (we recommend **2 XLM** to cover transaction fees).

### Activation Options

**Option 1: Request Activation from UBEC (Easiest)**
- Contact your Community Organizer or UBEC team
- Share your public key (the "G" address)
- We can send activation XLM as part of onboarding

**Option 2: Purchase XLM from an Exchange**
1. Create an account on a cryptocurrency exchange:
   - [Coinbase](https://www.coinbase.com/)
   - [Binance](https://www.binance.com/)
   - [Kraken](https://www.kraken.com/)
2. Purchase approximately $1-2 worth of XLM
3. Withdraw XLM to your wallet's public key
4. Your wallet is now active!

**Option 3: Ask a Community Member**
- If you know someone already in UBEC
- They can send you activation XLM
- Share only your public key (never your secret key!)

---

## Step 4: Set Up UBEC Trustlines

Before you can receive UBEC tokens, you must "trust" each token. This is a Stellar security feature that prevents unwanted tokens from being sent to your wallet.

### Understanding Trustlines

- Each trustline costs a small amount of XLM (locked, not spent)
- You need one trustline per token type
- Four UBEC tokens = four trustlines needed

### UBEC Token Details

| Token | Code | Element | Issuer Address |
|-------|------|---------|----------------|
| **UBEC** | UBEC | 🌬️ Air | `GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCCSIKELEH7ORUCX5UB2VN` |
| **UBECrc** | UBECrc | 💧 Water | `GBYOTGM27KLFNQQU3G6QWVEK7LQB36N6OX2YLYMN4WU3AFM4VRFZUBEC` |
| **UBECgpi** | UBECgpi | 🌍 Earth | `GCPU3LUGRIYLWMPOQEEGIL2HI5Z637PQVK42Z5PYRRQMPFDTNT5SUBEC` |
| **UBECtt** | UBECtt | 🔥 Fire | `GBWYGECRQ7R5E6QQKWBTVNYSCFVTIYZLF6MGDHJQBHP2KU2U65Z5UBEC` |

### Adding Trustlines in Lobstr

1. Open Lobstr and go to **Assets**
2. Tap **Add Asset** or the **+** button
3. Search for "UBEC" or enter manually:
   - Asset Code: `UBEC`
   - Issuer: `GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCCSIKELEH7ORUCX5UB2VN`
4. Tap **Add** to confirm
5. Repeat for UBECrc, UBECgpi, and UBECtt

### Adding Trustlines in Solar Wallet

1. Go to **Account** → **Manage Assets**
2. Click **Add Asset**
3. Enter the Asset Code and Issuer address
4. Click **Add Trustline**
5. Confirm the transaction
6. Repeat for all four tokens

### Adding Trustlines in Freighter

1. Click the Freighter extension icon
2. Go to **Manage Assets**
3. Click **Add Asset**
4. Select **Add Manually**
5. Enter:
   - Asset Code: e.g., `UBEC`
   - Issuer Public Key: (paste from table above)
6. Click **Add Asset**
7. Repeat for all four tokens

### Adding Trustlines via Stellar Laboratory (Advanced)

1. Go to [laboratory.stellar.org](https://laboratory.stellar.org/)
2. Navigate to **Build Transaction**
3. Enter your public key as the source account
4. Add operation: **Change Trust**
5. Enter Asset Code and Issuer
6. Set limit (leave blank for default)
7. Sign with your secret key
8. Submit transaction

---

## Step 5: Verify Your Setup

### Checklist

- [ ] Wallet created and password set
- [ ] Secret key/recovery phrase written down on paper
- [ ] Secret key stored in a secure location
- [ ] Wallet activated with XLM
- [ ] UBEC trustline established
- [ ] UBECrc trustline established
- [ ] UBECgpi trustline established
- [ ] UBECtt trustline established

### Test Your Wallet

1. **Check your XLM balance** — Should show at least 1-2 XLM
2. **View your assets** — All four UBEC tokens should appear (with 0 balance until you receive them)
3. **Copy your public key** — Ready to share with UBEC for token distribution

---

## Security Best Practices

### ✅ DO

- **Write down your secret key on paper** — Physical backup is safest
- **Store backups in multiple secure locations** — Safe deposit box, fireproof safe
- **Use a strong, unique password** — For your wallet application
- **Verify addresses before sending** — Double-check recipient addresses
- **Start with small test transactions** — Before sending large amounts
- **Keep your wallet software updated** — Security patches are important
- **Use official wallet downloads only** — Avoid third-party sources

### ❌ DON'T

- **Never share your secret key** — Not with anyone, ever
- **Never store secret keys digitally** — No photos, screenshots, cloud storage, email
- **Never enter your secret key on websites** — Except official wallet interfaces
- **Never click links claiming "wallet verification"** — These are scams
- **Never give remote access to your device** — While your wallet is open

### ⚠️ Security Warnings

> **UBEC will NEVER ask for your secret key.** If anyone claiming to be from UBEC asks for your secret key, it is a scam. Report it immediately.

> **Your secret key = complete control.** Anyone with your secret key can take all your tokens. There is no recovery if your key is compromised.

> **Lost secret key = lost funds.** If you lose your secret key and cannot access your wallet, your tokens are gone forever. There is no reset or recovery.

---

## Troubleshooting

### "My wallet won't activate"

- Ensure you've sent at least 1 XLM to your public key
- Check that you're using the correct public key (starts with "G")
- Wait a few minutes — blockchain confirmations can take time
- Verify the sending exchange/wallet completed the transaction

### "I can't add a trustline"

- You need XLM in your wallet to create trustlines
- Each trustline requires ~0.5 XLM to be reserved
- Ensure you have enough XLM for all four trustlines plus transaction fees
- Double-check the asset code and issuer address for typos

### "Trustline shows but I can't receive tokens"

- Verify the trustline issuer matches exactly (case-sensitive)
- Check that the trustline is active (not pending)
- Contact support with your public key to verify

### "Transaction failed"

- Check your XLM balance covers the transaction fee
- Verify the recipient address is correct
- Ensure the recipient has a trustline for the token you're sending
- Check network status at [stellar.expert](https://stellar.expert/)

### "I lost my secret key"

- If you have your recovery phrase, you can restore your wallet
- If you have no backup, unfortunately there is no recovery
- **Prevention is key** — Always backup before funding your wallet

---

## Next Steps

Once your wallet is set up and trustlines are established:

1. **Share your public key** with your Community Organizer or UBEC team
2. **Complete your onboarding** via the participation guide
3. **Receive your first UBEC tokens** — Welcome to the commons!
4. **Explore the ecosystem** through the four element guides

### Continue Your Journey

- 🌬️ [Air Gateway Guide](/docs/guides/air-gateway-guide) — Start with UBEC tokens
- 💧 [Water Reciprocity Guide](/docs/guides/water-reciprocity-guide) — Participate in reciprocity
- 🌍 [Earth Mutualism Guide](/docs/guides/earth-mutualism-guide) — Build stable relationships
- 🔥 [Fire Regeneration Guide](/docs/guides/fire-regeneration-guide) — Create regenerative impact

### Additional Resources

- 📚 [Complete Onboarding Guide](/docs/guides/onboarding-user-guides)
- 💰 [Token Holders Guide](/docs/guides/token-holders-guide)
- 🏛️ [Governance Participant Guide](/docs/guides/governance-guide)
- 👥 [Community Organizer Guide](/docs/guides/community-organizer-guide)

---

## Quick Reference Card

### Your Wallet Information

| Item | Your Value |
|------|------------|
| **Wallet App** | _________________ |
| **Public Key** | G_________________ |
| **Backup Location** | _________________ |

### UBEC Token Issuers (Copy/Paste)

```
UBEC:    GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCCSIKELEH7ORUCX5UB2VN
UBECrc:  GBYOTGM27KLFNQQU3G6QWVEK7LQB36N6OX2YLYMN4WU3AFM4VRFZUBEC
UBECgpi: GCPU3LUGRIYLWMPOQEEGIL2HI5Z637PQVK42Z5PYRRQMPFDTNT5SUBEC
UBECtt:  GBWYGECRQ7R5E6QQKWBTVNYSCFVTIYZLF6MGDHJQBHP2KU2U65Z5UBEC
```

---

*Your wallet is your gateway to the Ubuntu Bioregional Economic Commons. Keep it secure, and welcome to the journey!* 🔐

---

**Attribution:** This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

**Document Version:** 1.0  
**Created:** December 2025
