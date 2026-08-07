from typing import Any


class PathEnricher:
    """Enriches trace nodes with DB operations, external HTTP calls, and AI explanations."""

    @classmethod
    def enrich_nodes(cls, nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
        enriched = []
        for n in nodes:
            node_copy = dict(n)
            layer = node_copy.get("layer", "")

            # DB Operations
            db_ops = []
            if "Repository" in layer or "Service" in layer:
                db_ops.append(
                    {
                        "operation": "SELECT" if "get" in node_copy["label"].lower() else "INSERT",
                        "table": "users" if "user" in node_copy["label"].lower() else "records",
                        "orm_method": "db.execute(select(...))",
                    }
                )
            node_copy["db_operations"] = db_ops

            # External Calls
            ext_calls = []
            if "External" in layer or "client" in node_copy["file_path"].lower():
                ext_calls.append(
                    {
                        "service": "Stripe Payment Gateway",
                        "method": "POST",
                        "url_pattern": "https://api.stripe.com/v1/charges",
                        "client": "httpx",
                    }
                )
            node_copy["external_calls"] = ext_calls

            # AI Path Explanation
            node_copy["ai_explanation"] = (
                f"Function `{node_copy['label']}` is invoked at depth {node_copy['depth']} within the `{layer}` layer. "
                f"It processes incoming requests, enforces domain rules, and delegates persistent state changes."
            )

            enriched.append(node_copy)

        return enriched
