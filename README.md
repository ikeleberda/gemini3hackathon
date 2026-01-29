# Fractal Aphelion

**Fractal Aphelion** is an autonomous multi-agent content generation system powered by Google Gemini. It automates the process of researching, writing, optimizing, and publishing high-quality content to WordPress websites.

## 🚀 Key Features

*   **Multi-Agent Workflow**: Orchestrates specialized AI agents for different stages of content creation:
    *   **Manager Agent**: Coordinates the workflow and handles high-level decision making.
    *   **Research Agent**: Gathers accurate information and sources from the web.
    *   **Writer Agent**: drafts engaging and structured content.
    *   **SEO Agent**: Optimizes content for search engines (keywords, meta tags, etc.).
    *   **Media Agent**: Generates or sources relevant images.
    *   **Publisher Agent**: Formats and publishes the final post to WordPress.
*   **Content Scheduling**: Plan your content strategy by scheduling agent runs for specific dates and times in your local timezone.
*   **Content Calendar**: Visual dashboard to manage, edit, and delete scheduled topics.
*   **WordPress Integration**: Seamlessly connects to WordPress sites via Application Passwords.
*   **Google Gemini Powered**: Utilizes the latest Gemini models (Flash, Pro) for high-performance generation.
*   **Cloud Native**: Designed for deployment on Google Cloud Run with PostgreSQL.

## 🛠️ Tech Stack

*   **Backend**: Python (Flask)
*   **Frontend**: Next.js, TypeScript, Tailwind CSS
*   **Database**: PostgreSQL (Prisma ORM)
*   **AI Models**: Google Gemini via Google Gen AI SDK
*   **Infrastructure**: Google Cloud Run, Cloud Build

## 📦 Project Structure

```
fractal-aphelion/
├── app.py                 # Flask backend entry point
├── main.py                # Agent workflow entry point
├── src/
│   ├── agents/            # Agent implementations (Manager, Writer, etc.)
│   ├── adk/               # Agent Development Kit (core logic)
│   └── tools/             # Agent tools (Search, etc.)
├── web/                   # Next.js Frontend application
│   ├── app/               # App Router pages and API routes
│   └── prisma/            # Database schema
├── test/                  # Test scripts
└── DEPLOYMENT.md          # Deployment guide
```

## 🚀 Getting Started

### Prerequisites

*   Python 3.9+
*   Node.js 18+
*   PostgreSQL
*   Google Cloud SDK (for deployment)

### Local Development

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/fractal-aphelion.git
    cd fractal-aphelion
    ```

2.  **Backend Setup**:
    ```bash
    # Create virtual environment
    python -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate on Windows

    # Install dependencies
    pip install -r requirements.txt

    # Run the backend
    python app.py
    ```

3.  **Frontend Setup**:
    ```bash
    cd web

    # Install dependencies
    npm install

    # Setup database (ensure .env is configured)
    npx prisma generate
    npx prisma db push

    # Run the frontend
    npm run dev
    ```

## ☁️ Deployment

For detailed deployment instructions on Google Cloud Platform, please refer to [DEPLOYMENT.md](DEPLOYMENT.md).

## 📄 License

[MIT License](LICENSE)
