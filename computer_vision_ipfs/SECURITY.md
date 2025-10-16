# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in this project, please email security@example.com instead of using the issue tracker.

Please include the following information:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Security Best Practices

When using this project:

1. **Private Keys**: Never commit private keys to version control
2. **Environment Variables**: Use `.env` files (never commit them)
3. **Dependencies**: Keep dependencies up to date: `pip install --upgrade -r requirements.txt`
4. **Wallet Security**: Use hardware wallets in production
5. **Contract Audits**: Always audit smart contracts before deployment
6. **Testnet Only**: Test extensively on testnet before mainnet deployment

## Cardano Specific

- Use Cardano testnet for development
- Verify wallet ownership before transactions
- Monitor transaction status on blockchain explorer
- Keep Cardano node software updated

## IPFS Security

- Use pinning services for critical data
- Verify content hashes before usage
- Implement access controls for sensitive data

## Compliance

- Comply with local regulations
- Implement KYC/AML if required
- Secure all user data appropriately
