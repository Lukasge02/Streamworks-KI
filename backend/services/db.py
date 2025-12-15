import os
import json
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


class DatabaseService:
    _instance = None
    client: Optional[Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseService, cls).__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if url and key:
            try:
                self.client = create_client(url, key)
            except Exception as e:
                print(f"Error connecting to Supabase: {e}")
        else:
            print("Warning: SUPABASE_URL or SUPABASE_KEY not found in environment.")

    def get_client(self) -> Optional[Client]:
        return self.client

    def save_session(self, session_id: str, data: dict):
        """Save or update a wizard session."""
        if not self.client:
            return None
        try:
            # Upsert session data
            data_copy = json.loads(
                json.dumps(data, default=str)
            )  # Ensure JSON serializable
            return (
                self.client.table("sessions")
                .upsert({"id": session_id, "data": data_copy, "updated_at": "now()"})
                .execute()
            )
        except Exception as e:
            print(f"Error saving session {session_id}: {e}")
            return None

    def get_session(self, session_id: str) -> Optional[dict]:
        """Retrieve a wizard session."""
        if not self.client:
            return None
        try:
            response = (
                self.client.table("sessions")
                .select("data")
                .eq("id", session_id)
                .execute()
            )
            if response.data and len(response.data) > 0:
                return response.data[0]["data"]
            return None
        except Exception as e:
            print(f"Error getting session {session_id}: {e}")
            return None

    def save_stream(
        self,
        filename: str,
        content: str,
        metadata: dict = None,
        job_type: str = "STANDARD",
    ):
        """Save a generated stream."""
        if not self.client:
            return None

        dataset = {
            "filename": filename,
            "content": content,
            "metadata": metadata or {},
        }

        # Check if schema supports job_type directly or inside metadata
        # Based on migration, we have metadata jsonb. job_type can go there.
        if metadata is None:
            metadata = {}
        metadata["job_type"] = job_type
        dataset["metadata"] = metadata

        try:
            return self.client.table("streams").insert(dataset).execute()
        except Exception as e:
            print(f"Error saving stream {filename}: {e}")
            raise e

    def get_dropdown_options(self, category: str):
        """Fetch dropdown options for a specific category."""
        if not self.client:
            return []
        try:
            response = (
                self.client.table("dropdown_options")
                .select("label, value")
                .eq("category", category)
                .eq("is_active", True)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"Error fetching dropdown options for {category}: {e}")
            return []

    def get_user_streams(self, user_id: str = None, limit: int = 50):
        """Get recent streams (optionally filtered by user)"""
        if not self.client:
            return []
        try:
            query = (
                self.client.table("streams")
                .select("id, filename, created_at, metadata")
                .order("created_at", desc=True)
                .limit(limit)
            )

            # If user_id provided (future)
            if user_id:
                query = query.eq("user_id", user_id)

            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error fetching streams: {e}")
            return []

    def get_stream(self, stream_id: str):
        """Get full stream details including content"""
        if not self.client:
            return None
        try:
            response = (
                self.client.table("streams").select("*").eq("id", stream_id).execute()
            )

            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error fetching stream {stream_id}: {e}")
            return None

    def list_sessions(self, limit: int = 50):
        """List all sessions with their status and params for dashboard"""
        if not self.client:
            return []
        try:
            response = (
                self.client.table("sessions")
                .select("id, data, created_at, updated_at")
                .order("updated_at", desc=True)
                .limit(limit)
                .execute()
            )

            # Transform data for frontend
            sessions = []
            for row in response.data or []:
                data = row.get("data", {})
                params = data.get("params", {})
                sessions.append(
                    {
                        "id": row["id"],
                        "name": params.get("stream_name") or "Entwurf",
                        "status": data.get("status", "draft"),
                        "job_type": data.get("detected_job_type")
                        or params.get("job_type", "STANDARD"),
                        "current_step": data.get("current_step", "basic_info"),
                        "completion_percent": data.get("completion_percent", 0),
                        "created_at": row.get("created_at"),
                        "updated_at": row.get("updated_at"),
                        "params": params,
                    }
                )
            return sessions
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []

    def update_session_status(self, session_id: str, status: str):
        """Update session status (draft/complete)"""
        if not self.client:
            return None
        try:
            # Get existing session
            session = self.get_session(session_id)
            if session:
                session["status"] = status
                return self.save_session(session_id, session)
            return None
        except Exception as e:
            print(f"Error updating session status: {e}")
            return None

    def delete_session(self, session_id: str):
        """Delete a session"""
        if not self.client:
            return False
        try:
            self.client.table("sessions").delete().eq("id", session_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False

    # --- Project & Testing Methods ---

    def create_project(self, name: str, description: str = None):
        """Create a new project."""
        if not self.client:
            return None
        try:
            return (
                self.client.table("projects")
                .insert({"name": name, "description": description})
                .execute()
            )
        except Exception as e:
            print(f"Error creating project: {e}")
            return None

    def list_projects(self):
        """List all projects."""
        if not self.client:
            return []
        try:
            return (
                self.client.table("projects")
                .select("*")
                .order("created_at", desc=True)
                .execute()
                .data
            )
        except Exception as e:
            print(f"Error listing projects: {e}")
            return []

    def get_project(self, project_id: str):
        """Get project details."""
        if not self.client:
            return None
        try:
            response = (
                self.client.table("projects").select("*").eq("id", project_id).execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting project {project_id}: {e}")
            return None

    def delete_project(self, project_id: str):
        """Delete a project."""
        if not self.client:
            return False
        try:
            self.client.table("projects").delete().eq("id", project_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting project {project_id}: {e}")
            return False

    def link_project_document(
        self,
        project_id: str,
        doc_id: str,
        category: str = "context",
        filename: str = None,
        rag_enabled: bool = True,
    ):
        """
        Link a document to a project with category and RAG scope.
        """
        if not self.client:
            return None

        data = {
            "project_id": project_id,
            "doc_id": doc_id,
            "category": category,
            "rag_enabled": rag_enabled,
        }
        if filename:
            data["filename"] = filename

        try:
            result = self.client.table("project_documents").insert(data).execute()
            return result
        except Exception as e:
            print(f"Error linking document to project: {e}")
            return None

    def get_project_documents(self, project_id: str):
        """Get documents linked to a project."""
        if not self.client:
            return []
        try:
            return (
                self.client.table("project_documents")
                .select("*")
                .eq("project_id", project_id)
                .execute()
                .data
            )
        except Exception as e:
            print(f"Error getting project documents: {e}")
            return []

    def save_test_plan(self, project_id: str, content: str):
        """Save a generated test plan."""
        if not self.client:
            return None
        try:
            return (
                self.client.table("test_plans")
                .insert({"project_id": project_id, "content": content})
                .execute()
            )
        except Exception as e:
            print(f"Error saving test plan: {e}")
            return None

    def update_test_plan(self, plan_id: str, content: str):
        """Update an existing test plan content."""
        if not self.client:
            return None
        try:
            return (
                self.client.table("test_plans")
                .update({"content": content})
                .eq("id", plan_id)
                .execute()
            )
        except Exception as e:
            print(f"Error updating test plan {plan_id}: {e}")
            return None

    def get_test_plans(self, project_id: str):
        """Get test plans for a project."""
        if not self.client:
            return []
        try:
            return (
                self.client.table("test_plans")
                .select("*")
                .eq("project_id", project_id)
                .order("created_at", desc=True)
                .execute()
                .data
            )
        except Exception as e:
            print(f"Error getting test plans: {e}")
            return []

    def unlink_project_document(self, project_id: str, doc_id: str) -> bool:
        """Remove a document link from a project."""
        if not self.client:
            return False
        try:
            self.client.table("project_documents").delete().eq(
                "project_id", project_id
            ).eq("doc_id", doc_id).execute()
            return True
        except Exception as e:
            print(f"Error unlinking document from project: {e}")
            return False

    def update_project_document_rag(
        self, project_id: str, doc_id: str, rag_enabled: bool
    ) -> bool:
        """Update RAG enabled status for a project document."""
        if not self.client:
            return False
        try:
            result = (
                self.client.table("project_documents")
                .update({"rag_enabled": rag_enabled})
                .eq("project_id", project_id)
                .eq("doc_id", doc_id)
                .execute()
            )
            return bool(result.data)
        except Exception as e:
            print(f"Error updating document RAG status: {e}")
            return False


# Global instance
db = DatabaseService()


# Backward compatibility
def get_supabase() -> Optional[Client]:
    return db.get_client()
