# Code Gen Agent

## Quick Links

- [Sequential agents - Agent Development Kit](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/)

## Prerequisites

You need to meet the following requirements.

- Python 3.10+
- [Poetry](https://python-poetry.org/)

## Quick Start

At first, you need to create a `.env` file as follows:

```bash
echo -e "GOOGLE_API_KEY=<put your api key>" > src/gen_code/.env
```

## Architecture

```mermaid
flowchart LR

Input --> sub_agents_1

subgraph SequentialAgent
    sub_agents_1 --> sub_agents_2 --> sub_agents_3
end

sub_agents_3 --> Output

%% Sub agents
sub_agents_1["Code Writer Agent"]
sub_agents_2["Code Reviewer Agent"]
sub_agents_3["Code Refactor Agent"]
```
