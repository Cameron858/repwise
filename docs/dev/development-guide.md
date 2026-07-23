# Development Guide

This guide covers setting up and working with the Repwise development environment.

## Prerequisites

- Python 3.10 or later
- `uv` package manager
- SQLite3
- Git

## Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd repwise
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Set up credentials**
   - Copy `example.env` to `.env` and configure as needed
   - Place Google Cloud service account credentials in `credentials/` directory

## Running the Agent Development Environment

The project includes AI agents built with the Google ADK framework. To run the agent web interface:

```bash
uv run adk web src/repwise/agents --port 8000
```

This command:
- Starts the ADK web server from the repository root
- Serves the agent interface on `http://localhost:8000`
- Watches for code changes in `src/repwise/agents`

### Customising the Port

To run on a different port:

```bash
uv run adk web src/repwise/agents --port 9000
```

## Project Structure

**Representive**

```
repwise/
├── src/repwise/
│   ├── agents/          # AI agent definitions
│   ├── tools/           # Database and utility tools for agents
│   ├── config.py        # Configuration management
│   ├── gcloud.py        # Google Cloud integration
│   └── ingest.py        # Data ingestion pipeline
├── notebooks/           # Jupyter notebooks for exploration
├── db/                  # SQLite database
├── docs/
│   └── dev/             # Development documentation
└── scripts/             # Utility scripts
```

## Database

### Creating and Populating the Database

Run the ingestion pipeline to create the database and load workout data from Google Sheets:

```bash
uv run ingest
```

OR

```bash
uv run python -m src.repwise.ingest
```

This will:
1. Fetch raw data from Google Sheets
2. Validate and normalise the data
3. Create the SQLite schema
4. Populate tables: `exercises`, `sessions`, `entries`
5. Create and populate the `_metadata` table with table descriptions

### Database Schema

- **sessions**: Workout session logs indexed by date
- **entries**: Exercise sets, reps, and weights linked to sessions
- **exercises**: Normalised lookup table of exercise names
- **_metadata**: Table descriptions for agent reference

## Agent Development

### Available Tools

Agents have access to database tools in `src/repwise/tools/`.

### Adding New Agents

1. Create a new agent directory under `src/repwise/agents/<agent-name>/`
2. Define the agent in `agent.py` using the Google ADK
3. Import tools from `src/repwise/tools` as needed
4. Run `uv run adk web src/repwise/agents --port 8000` to test
