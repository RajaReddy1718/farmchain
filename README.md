# FarmChain

FarmChain is a blockchain-powered traceability web app for registering farmers, batches, transport events, and verifying product history.

## Features

- Register farmers and batches
- Track transport and tamper events
- Generate QR codes for batch verification
- Verify product history through a web page or JSON API
- Installable PWA and Electron desktop wrapper

## Tech Stack

- FastAPI
- SQLite
- Hardhat / Ethereum local node
- Electron
- Progressive Web App (PWA)

## Running Locally

1. Install dependencies:
   - Python packages from your environment
   - Node dependencies with `npm install`
2. Start the app:
   - Run `run-app.bat` on Windows
3. Open the app at:
   - `http://127.0.0.1:8000/`

## Project Structure

- `main.py` — FastAPI app entrypoint
- `routes/` — API route handlers
- `static/` — web UI and PWA assets
- `contracts/` — Solidity smart contract
- `scripts/` — deployment scripts

## Notes

The app uses a local Hardhat node and local SQLite database for development.
