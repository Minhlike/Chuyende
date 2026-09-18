"""
Công cụ đồ thị đối số M4, Trình phát hiện chu trình & Trình xuất hình ảnh (Nhắc 5 Phần 40, 41, 42)
"""

from typing import List, Dict, Any, Optional, Set
from research_agent.schemas.reasoning import (
    ArgumentNode,
    ArgumentEdge,
    ArgumentGraph,
)
from research_agent.core.enums import (
    ArgumentNodeType,
    ArgumentEdgeType,
    IntellectualOwnership,
)


class ArgumentGraphEngine:
    """
    Xây dựng, xác thực và trực quan hóa các Biểu đồ đối số M4 đã nhập.
    Phát hiện các vòng hỗ trợ hình tròn và xuất sang Nàng tiên cá, DOT và JSON.
    """

    def build_graph(
        self,
        nodes: List[ArgumentNode],
        edges: List[ArgumentEdge],
        graph_id: str = "ARG_GRAPH_MAIN",
        roadmap_node: Optional[str] = None,
    ) -> ArgumentGraph:
        """
        Xây dựng và xác nhận một ArgumentGraph.
        """
        is_cyclic = self.detect_cycles(nodes, edges)
        root_claims = [n.node_id for n in nodes if n.node_type == ArgumentNodeType.CLAIM]
        
        # Tính điểm hoàn thiện: tỷ lệ các nút được hỗ trợ trên tổng số yêu cầu
        claim_nodes = {n.node_id for n in nodes if n.node_type == ArgumentNodeType.CLAIM}
        supported_claims = {e.target_node_id for e in edges if e.relation_type in [ArgumentEdgeType.SUPPORTS, ArgumentEdgeType.DERIVED_FROM]}
        completeness = len(supported_claims.intersection(claim_nodes)) / len(claim_nodes) if claim_nodes else 1.0

        return ArgumentGraph(
            graph_id=graph_id,
            roadmap_node=roadmap_node,
            nodes=nodes,
            edges=edges,
            completeness_score=round(completeness, 3),
            is_cyclic=is_cyclic,
            root_claims=root_claims,
        )

    def detect_cycles(self, nodes: List[ArgumentNode], edges: List[ArgumentEdge]) -> bool:
        """
        Kiểm tra các chu kỳ có định hướng giữa các mối quan hệ hỗ trợ/phụ thuộc.
        """
        adj: Dict[str, List[str]] = {n.node_id: [] for n in nodes}
        for e in edges:
            if e.source_node_id in adj:
                adj[e.source_node_id].append(e.target_node_id)

        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for n in nodes:
            if n.node_id not in visited:
                if dfs(n.node_id):
                    return True
        return False

    def to_mermaid(self, graph: ArgumentGraph) -> str:
        """
        Xuất biểu đồ dưới dạng sơ đồ Nàng tiên cá tương thích với GitHub.
        """
        lines = ["graph TD"]
        # Các lớp tạo kiểu nút
        lines.append("    classDef claim fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;")
        lines.append("    classDef evidence fill:#e8f5e9,stroke:#388e3c,stroke-width:2px;")
        lines.append("    classDef assumption fill:#fff8e1,stroke:#fbc02d,stroke-width:2px;")
        lines.append("    classDef counter fill:#ffebee,stroke:#d32f2f,stroke-width:2px;")

        for n in graph.nodes:
            clean_title = n.title.replace('"', "'")
            lines.append(f'    {n.node_id}["{clean_title} ({n.node_type.value})"]')

        for e in graph.edges:
            lines.append(f'    {e.source_node_id} -->|{e.relation_type.value}| {e.target_node_id}')

        return "\n".join(lines)

    def to_dot(self, graph: ArgumentGraph) -> str:
        """
        Xuất biểu đồ dưới định dạng Graphviz DOT.
        """
        lines = ["digraph ArgumentGraph {", "    rankdir=LR;", "    node [shape=box, style=rounded];"]
        for n in graph.nodes:
            clean_title = n.title.replace('"', '\\"')
            lines.append(f'    "{n.node_id}" [label="{clean_title}\\n[{n.node_type.value}]"];')

        for e in graph.edges:
            lines.append(f'    "{e.source_node_id}" -> "{e.target_node_id}" [label="{e.relation_type.value}"];')

        lines.append("}")
        return "\n".join(lines)
