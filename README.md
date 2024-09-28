# RAG Pipeline Project

[![Contributors][contributors-shield]][contributors-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]

## Introduction

Welcome to the RAG Pipeline Project! This project integrates information retrieval techniques with generative models to provide comprehensive and accurate responses to user queries. 

## Table of Contents

1. [Features](#features)
2. [Flow Chart](#flow-chart)
3. [Built With](#built-with)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Project Checklist](#project-checklist)

## Features

- **Web Scraper**: Automatically scrapes and extracts information from web pages.
- **Chunking**: Breaks down large texts into manageable chunks for processing.
- **Content Page Parser**: Parses content pages and generates hierarchial tree data structures.
- **Dense Search on Database**: Performs dense vector searches on the database.
- **Sparse Search on Database**: Performs sparse vector searches on the database.
- **Reranking**: Reranks search results to improve relevance.
- **Prompt Engineering**: Crafts prompts for the final LLM query.
- **Langsmith Tracing**: Tracks and traces the pipeline processing.
- **Agency**: Makes decisions to branch, improves prompts and enhances pipeline.
- **Guard Rails**: Ensures the conversation with the chatbot follows company policies.

## Flow chart
[![Flowchart][flowchart-screenshot]](https://github.com/RaghaRao314159/Auditbot_backend)

## Built With

* [![Python][Python]][Python-url]
* [![LangChain][LangChain]][LangChain-url]
* [![Chroma][Chroma]][Chroma-url]
* [![elastic][elastic]][elastic-url]
* [![OpenAi][OpenAi]][OpenAi-url]
* [![Hugging Face][HuggingFace]][HuggingFace-url]

## Install Dependencies with conda

Use option 1 or option 2 to create a conda environment to run almost everything in this repo. 

**Option 1: Use requirements.txt**:
    ```
    conda create --name <env> --file requirements.txt
    ```

**Option 2: Use environment.yml**:
    ```
    conda env create -f environment.yml
    ```

Just for ["../experiments/recursive_retrieval.ipynb"](../experiments/recursive_retrieval.ipynb) and ["../utils/llama_index_utils.py"](../utils/llama_index_utils.py), a seperate environment is required.

**LlamaIndex env: Use requirements_recursive_retrieval.txt**:
    ```
    conda create --name <env> --file requirements_recursive_retrieval.txt
    ```

## Tutorial

After installing the necessary dependencies, you can follow along the tutorial series (in the turorial directory) to build a chatbot in the following order. Remember to substitute the dummy openai api key with your own. The frontend for this repository is in [AuditBot_frontend](https://github.com/RaghaRao314159/AuditBot_frontend)

```sh
1. data_processing.ipynb
2. database_setup.ipynb
3. RAG.ipynb
4. addOns-improvements-experiments.ipynb
5. production.ipynb
```

## Acknowledgements

I am extremely grateful to Tay Jun Jie for his guidance on this project.

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/RaghaRao314159/Auditbot_backend.svg?style=for-the-badge
[contributors-url]: https://github.com/RaghaRao314159/Auditbot_backend/graphs/contributors
[stars-shield]: https://img.shields.io/github/stars/RaghaRao314159/Auditbot_backend.svg?style=for-the-badge
[stars-url]: https://github.com/RaghaRao314159/Auditbot_backend/stargazers
[issues-shield]: https://img.shields.io/github/issues/RaghaRao314159/Auditbot_backend.svg?style=for-the-badge
[issues-url]: https://github.com/RaghaRao314159/Auditbot_backend/issues
[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org
[LangChain]: https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=ffffff
[LangChain-url]: https://www.langchain.com
[OpenAi]: https://img.shields.io/badge/OpenAi-412991?style=for-the-badge&logo=openai&logoColor=ffffff
[OpenAi-url]: https://openai.com
[Chroma]: https://img.shields.io/badge/Chroma-ffffff?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB3aWR0aD0iMjA5IiBoZWlnaHQ9IjEzNSIgdmlld0JveD0iMCAwIDIwOSAxMzUiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxlbGxpcHNlIGN4PSIxMzYuMDE5IiBjeT0iNjcuMjMwNCIgcng9IjY2LjY2NjciIHJ5PSI2NCIgZmlsbD0iI0ZGREUyRCIvPgo8ZWxsaXBzZSBjeD0iNjkuMzUyIiBjeT0iNjcuMjMwNCIgcng9IjY2LjY2NjciIHJ5PSI2NCIgZmlsbD0iIzMyN0VGRiIvPgo8cGF0aCBkPSJNMi42ODUyOCA2Ny4yMzA0QzIuNjg1MjcgMzEuODg0MiAzMi41MzI5IDMuMjMwNDcgNjkuMzUxOSAzLjIzMDQ3TDY5LjM1MTkgNjcuMjMwNEwyLjY4NTI4IDY3LjIzMDRaIiBmaWxsPSIjMzI3RUZGIi8+CjxwYXRoIGQ9Ik0xMzYuMDE5IDY3LjIzMDVDMTM2LjAxOSAxMDIuNTc3IDEwNi4xNzEgMTMxLjIzIDY5LjM1MTkgMTMxLjIzTDY5LjM1MTkgNjcuMjMwNUwxMzYuMDE5IDY3LjIzMDVaIiBmaWxsPSIjRkY2NDQ2Ii8+CjxwYXRoIGQ9Ik02OS4zNTIgNjcuMjMwNEM2OS4zNTIgMzEuODg0MiA5OS4xOTk3IDMuMjMwNDcgMTM2LjAxOSAzLjIzMDQ3TDEzNi4wMTkgNjcuMjMwNEw2OS4zNTIgNjcuMjMwNFoiIGZpbGw9IiNGRjY0NDYiLz4KPC9zdmc+Cg==
[Chroma-url]: https://www.trychroma.com
[elastic]: https://img.shields.io/badge/elastic-131c3d?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzMiAzMiIgd2lkdGg9IjY0IiBoZWlnaHQ9IjY0Ij48cGF0aCBkPSJNMzIgMTYuNzdjMC0yLjY3OC0xLjY2NC01LjAzLTQuMTY2LTUuOTM3YTkuMTQgOS4xNCAwIDAgMCAuMTYyLTEuNzE4YzAtNS00LjA1Ny05LjA0OC05LjAzNS05LjA0OC0yLjkyIDAtNS42MjYgMS4zOTMtNy4zMyAzLjc0NmE0Ljc4IDQuNzggMCAwIDAtMi45MzUtMWMtMi42NSAwLTQuOCAyLjE1LTQuOCA0LjggMCAuNTgyLjEwOCAxLjE1LjI5OCAxLjY3N0E2LjM2IDYuMzYgMCAwIDAgMCAxNS4yNDNhNi4zMSA2LjMxIDAgMCAwIDQuMTc5IDUuOTUxIDkuMDIgOS4wMiAwIDAgMC0uMTYyIDEuNzE4IDkuMDMgOS4wMyAwIDAgMCA5LjAyMSA5LjAyMWMyLjkyIDAgNS42MjYtMS40MDcgNy4zMTctMy43Ni44NC42NjMgMS44NjYgMS4wMjggMi45MzUgMS4wMjggMi42NSAwIDQuOC0yLjE1IDQuOC00LjggMC0uNTgyLS4xMDgtMS4xNS0uMjk4LTEuNjc3QTYuMzcgNi4zNyAwIDAgMCAzMiAxNi43NzEiIGZpbGw9IiNmZmYiLz48cGF0aCBkPSJNMTIuNTc4IDEzLjc5NWw3LjAwNiAzLjE5MiA3LjA2LTYuMTk0YTcuNCA3LjQgMCAwIDAgLjE0OS0xLjU1NSA3LjkxIDcuOTEgMCAwIDAtNy44OTktNy44OTkgNy44OSA3Ljg5IDAgMCAwLTYuNTA1IDMuNDM1bC0xLjE3NyA2LjF6IiBmaWxsPSIjZmVkMTBhIi8+PHBhdGggZD0iTTUuMzMgMjEuMjA3YTcuNjYgNy42NiAwIDAgMC0uMTUgMS41ODJjMCA0LjM3IDMuNTU3IDcuOTEyIDcuOTI2IDcuOTEyYTcuOTIgNy45MiAwIDAgMCA2LjU0Ni0zLjQ2MmwxLjE2My02LjA3My0xLjU1NS0yLjk3NS03LjAzMy0zLjIwNXoiIGZpbGw9IiMyNGJiYjEiLz48cGF0aCBkPSJNNS4yODggOS4wOWw0LjggMS4xMzYgMS4wNTUtNS40NWMtLjY1LS41LTEuNDYtLjc3LTIuMy0uNzdBMy43OSAzLjc5IDAgMCAwIDUuMDU4IDcuNzljMCAuNDQ2LjA4Ljg5My4yMyAxLjI5OCIgZmlsbD0iI2VmNTA5OCIvPjxwYXRoIGQ9Ik00Ljg3IDEwLjIzOGMtMi4xMzcuNzAzLTMuNjM4IDIuNzYtMy42MzggNS4wMTggMCAyLjIwNSAxLjM2NiA0LjE2NiAzLjQwOCA0Ljk1bDYuNzM1LTYuMDg2LTEuMjMtMi42Mzd6IiBmaWxsPSIjMTdhOGUwIi8+PHBhdGggZD0iTTIwLjg3IDI3LjI0YTMuOCAzLjggMCAwIDAgMi4yODYuNzg0IDMuNzkgMy43OSAwIDAgMCAzLjc4Ny0zLjc4NyAzLjgyIDMuODIgMCAwIDAtLjIzLTEuMzEybC00Ljc4OC0xLjEyM3oiIGZpbGw9IiM5M2M4M2UiLz48cGF0aCBkPSJNMjEuODQzIDIwLjU0NGw1LjI3NSAxLjIzYTUuMzMgNS4zMyAwIDAgMCAzLjYzOC01LjAzMSA1LjI5IDUuMjkgMCAwIDAtMy40MDgtNC45MzdsLTYuODk4IDYuMDQ2eiIgZmlsbD0iIzA3NzlhMSIvPjwvc3ZnPg==
[elastic-url]: https://www.elastic.co
[HuggingFace]: https://img.shields.io/badge/Hugging%20Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=e8570e
[HuggingFace-url]: https://huggingface.co
[flowchart-screenshot]: flowchart.png
