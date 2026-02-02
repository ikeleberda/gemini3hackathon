import abc
import typing
from dataclasses import dataclass, field

# Try to import from the official google-adk
try:
    from google.adk import BaseAgent as OfficialBaseAgent
    from google.adk import AgentContext as OfficialAgentContext
    print("[ADK] Using official google-adk classes.")
    
    def _update_db_logs(context_obj):
        """Helper to update database logs in real-time."""
        if not (context_obj.db_url and context_obj.job_id):
            return

        try:
            # Extract current step (last agent tag)
            lines = "\n".join(context_obj.history).strip().split("\n")
            current_step = None
            import re
            for i in range(len(lines)-1, -1, -1):
                match = re.match(r"^\[([^\]]+)\]\s*(.*)$", lines[i].strip())
                if match:
                    current_step = f"{match.group(1)}: {match.group(2)}"[:100]
                    break

            if context_obj.db_url.startswith("file:") or "sqlite" in context_obj.db_url.lower():
                import sqlite3
                db_path = context_obj.db_url.replace("file:", "")
                if "?" in db_path: db_path = db_path.split("?")[0]
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                cur.execute(
                    'UPDATE "AgentJob" SET "logs" = ?, "currentStep" = ?, "updatedAt" = CURRENT_TIMESTAMP WHERE "id" = ?',
                    ("\n".join(context_obj.history), current_step, context_obj.job_id)
                )
            else:
                import psycopg2
                from urllib.parse import urlparse, parse_qs, unquote
                parsed = urlparse(context_obj.db_url)
                params = parse_qs(parsed.query)
                
                # Robust parsing for Prisma-style URLs and Unix sockets
                host = params.get('host', [None])[0] or parsed.hostname
                
                connect_params = {
                    "dbname": parsed.path.lstrip('/'),
                    "user": parsed.username,
                    "password": unquote(parsed.password) if parsed.password else None,
                    "host": host
                }
                connect_params = {k: v for k, v in connect_params.items() if v is not None}
                
                conn = psycopg2.connect(**connect_params)
                cur = conn.cursor()
                cur.execute(
                    'UPDATE "AgentJob" SET "logs" = %s, "currentStep" = %s, "updatedAt" = NOW() WHERE "id" = %s',
                    ("\n".join(context_obj.history), current_step, context_obj.job_id)
                )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as db_err:
            print(f"[DB LOG ERROR] {db_err}")

    class AgentContext(OfficialAgentContext):
        """Adapter for AgentContext."""
        def __init__(self):
            # Custom initialization
            self.history = []
            self.topic = ""
            self.is_simulated = False
            self.google_api_key = None
            self.db_url = None
            self.job_id = None
            super().__init__()

        def log(self, message: str):
            self.history.append(message)
            try:
                print(f"[System Log] {message}")
            except Exception:
                pass
            _update_db_logs(self)

    class BaseAgent(OfficialBaseAgent):
        """Adapter for BaseAgent."""
        def __init__(self, name: str, context: AgentContext, config: typing.Dict[str, typing.Any] = None):
            super().__init__(name=name)
            self.context = context
            self.config = config or {}

        def log(self, message: str):
            self.context.log(f"[{self.name}] {message}")

except ImportError:
    print("[ADK] Official google-adk not found or incompatible. Using local shim.")
    
    def _update_db_logs(context_obj):
        """Helper to update database logs in real-time."""
        if not (context_obj.db_url and context_obj.job_id):
            return

        try:
            # Extract current step (last agent tag)
            lines = "\n".join(context_obj.history).strip().split("\n")
            current_step = None
            import re
            for i in range(len(lines)-1, -1, -1):
                match = re.match(r"^\[([^\]]+)\]\s*(.*)$", lines[i].strip())
                if match:
                    current_step = f"{match.group(1)}: {match.group(2)}"[:100]
                    break

            if context_obj.db_url.startswith("file:") or "sqlite" in context_obj.db_url.lower():
                import sqlite3
                db_path = context_obj.db_url.replace("file:", "")
                if "?" in db_path: db_path = db_path.split("?")[0]
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                cur.execute(
                    'UPDATE "AgentJob" SET "logs" = ?, "currentStep" = ?, "updatedAt" = CURRENT_TIMESTAMP WHERE "id" = ?',
                    ("\n".join(context_obj.history), current_step, context_obj.job_id)
                )
            else:
                import psycopg2
                from urllib.parse import urlparse, parse_qs, unquote
                parsed = urlparse(context_obj.db_url)
                params = parse_qs(parsed.query)
                
                # Robust parsing for Prisma-style URLs and Unix sockets
                host = params.get('host', [None])[0] or parsed.hostname
                
                connect_params = {
                    "dbname": parsed.path.lstrip('/'),
                    "user": parsed.username,
                    "password": unquote(parsed.password) if parsed.password else None,
                    "host": host
                }
                connect_params = {k: v for k, v in connect_params.items() if v is not None}
                
                conn = psycopg2.connect(**connect_params)
                cur = conn.cursor()
                cur.execute(
                    'UPDATE "AgentJob" SET "logs" = %s, "currentStep" = %s, "updatedAt" = NOW() WHERE "id" = %s',
                    ("\n".join(context_obj.history), current_step, context_obj.job_id)
                )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as db_err:
            print(f"[DB LOG ERROR] {db_err}")

    # Fallback / Shim Implementation
    @dataclass
    class AgentContext:
        """Shared context for the agent system."""
        state: typing.Dict[str, typing.Any] = field(default_factory=dict)
        history: typing.List[str] = field(default_factory=list)
        topic: str = ""
        is_simulated: bool = False
        db_url: str = None
        job_id: str = None
        google_api_key: str = None

        def log(self, message: str):
            self.history.append(message)
            try:
                print(f"[System Log] {message}")
            except Exception:
                pass
            _update_db_logs(self)

    class BaseAgent(abc.ABC):
        """Abstract base class for all agents."""
        
        def __init__(self, name: str, context: AgentContext, config: typing.Dict[str, typing.Any] = None):
            self.name = name
            self.context = context
            self.config = config or {}

        @abc.abstractmethod
        def run(self, input_data: typing.Any) -> typing.Any:
            """Execute the agent's logic."""
            pass

        def log(self, message: str):
            """Log a message prefixed with the agent's name."""
            self.context.log(f"[{self.name}] {message}")
