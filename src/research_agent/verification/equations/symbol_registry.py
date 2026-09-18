"""
Người kiểm tra phạm vi toán học và đăng ký ký hiệu (Lời nhắc 6 Phần 10)
"""

from typing import Dict, List, Optional, Tuple
from research_agent.schemas.verification import ScopedSymbol


class SymbolRegistry:
    """
    Quản lý các ký hiệu toán học trên các phương trình và không gian tên.
    Đảm bảo không có giả định sai về ngữ nghĩa tương đương giữa các chữ cái ký hiệu giống hệt nhau.
    """

    def __init__(self):
        self._symbols: Dict[str, ScopedSymbol] = {}

    def register_symbol(self, symbol: ScopedSymbol) -> ScopedSymbol:
        """Đăng ký một định nghĩa ký hiệu toán học có phạm vi."""
        self._symbols[symbol.symbol_id] = symbol
        return symbol

    def get_symbol(self, symbol_id: str) -> Optional[ScopedSymbol]:
        return self._symbols.get(symbol_id)

    def list_symbols(self, equation_id: Optional[str] = None) -> List[ScopedSymbol]:
        if equation_id:
            return [s for s in self._symbols.values() if s.equation_id == equation_id]
        return list(self._symbols.values())

    def detect_symbol_ambiguity(
        self,
        symbol_latex: str,
    ) -> List[Tuple[ScopedSymbol, ScopedSymbol, str]]:
        r"""
        Phát hiện xem chuỗi ký hiệu giống nhau (e.g. '\lambda') có ý nghĩa xung đột hay không
        trên các phương trình khác nhau mà không có không gian tên rõ ràng.
        """
        matching = [s for s in self._symbols.values() if s.symbol_latex == symbol_latex]
        ambiguities = []
        for i in range(len(matching)):
            for j in range(i + 1, len(matching)):
                s1, s2 = matching[i], matching[j]
                if s1.name.lower() != s2.name.lower() or s1.domain != s2.domain:
                    ambiguities.append((
                        s1,
                        s2,
                        f"Symbol '{symbol_latex}' means '{s1.name}' in {s1.equation_id or 'global'} but '{s2.name}' in {s2.equation_id or 'global'}."
                    ))
        return ambiguities

    def audit_symbol_completeness(self, symbol: ScopedSymbol) -> List[str]:
        """Kiểm tra xem biểu tượng đã đăng ký có đủ ngữ cảnh vật lý và toán học hay không."""
        issues = []
        if not symbol.name or len(symbol.name.strip()) < 2:
            issues.append(f"Symbol '{symbol.symbol_latex}' has empty or trivial name.")
        if not symbol.domain and not symbol.shape_or_dimension:
            issues.append(f"Symbol '{symbol.symbol_latex}' lacks both mathematical domain and dimension.")
        return issues
