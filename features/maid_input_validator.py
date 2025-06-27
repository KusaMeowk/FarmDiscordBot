"""
Maid System Input Validator
Validation functions cho tất cả user inputs trong maid system
"""
import re
import difflib
from typing import Tuple, List, Dict, Any

class MaidInputValidator:
    """Input validator cho maid system"""
    
    # Constants
    MAX_NAME_LENGTH = 50
    MIN_NAME_LENGTH = 2
    DANGEROUS_CHARS = ['<', '>', '"', "'", '&', '`', '{', '}', '[', ']', '\\', '/']
    SCRIPT_PATTERNS = ['script', 'javascript', 'eval', 'function', 'onclick', 'onload', 'onerror']
    
    @staticmethod
    def validate_maid_name(name: str) -> Tuple[bool, str]:
        """
        Validate maid custom name
        
        Args:
            name: Custom name để validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "❌ Tên không được để trống"
        
        name = name.strip()
        
        # Check length
        if len(name) > MaidInputValidator.MAX_NAME_LENGTH:
            return False, f"❌ Tên không được dài quá {MaidInputValidator.MAX_NAME_LENGTH} ký tự"
        
        if len(name) < MaidInputValidator.MIN_NAME_LENGTH:
            return False, f"❌ Tên phải có ít nhất {MaidInputValidator.MIN_NAME_LENGTH} ký tự"
        
        # Check for dangerous characters
        if any(char in name for char in MaidInputValidator.DANGEROUS_CHARS):
            return False, "❌ Tên chứa ký tự không hợp lệ"
        
        # Check for script injection attempts
        name_lower = name.lower()
        if any(pattern in name_lower for pattern in MaidInputValidator.SCRIPT_PATTERNS):
            return False, "❌ Tên chứa nội dung không hợp lệ"
        
        # Check for excessive whitespace
        if '  ' in name or name != name.strip():
            return False, "❌ Tên không được có khoảng trắng thừa"
        
        # Check for numbers only
        if name.isdigit():
            return False, "❌ Tên không được chỉ toàn số"
        
        return True, ""
    
    @staticmethod
    def validate_search_query(query: str) -> Tuple[bool, str]:
        """
        Validate search query
        
        Args:
            query: Search query để validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not query or not query.strip():
            return False, "❌ Từ khóa tìm kiếm không được để trống"
        
        query = query.strip()
        
        if len(query) < 1:
            return False, "❌ Từ khóa tìm kiếm quá ngắn"
        
        if len(query) > 100:
            return False, "❌ Từ khóa tìm kiếm quá dài"
        
        # Allow more characters for search but still prevent injection
        dangerous_patterns = ['<script', 'javascript:', 'eval(', 'function(']
        query_lower = query.lower()
        if any(pattern in query_lower for pattern in dangerous_patterns):
            return False, "❌ Từ khóa tìm kiếm chứa nội dung không hợp lệ"
        
        return True, ""
    
    @staticmethod
    def sanitize_name(name: str) -> str:
        """
        Sanitize name input
        
        Args:
            name: Name để sanitize
            
        Returns:
            str: Sanitized name
        """
        if not name:
            return ""
        
        # Strip whitespace
        name = name.strip()
        
        # Remove dangerous characters
        for char in MaidInputValidator.DANGEROUS_CHARS:
            name = name.replace(char, '')
        
        # Remove multiple spaces
        name = re.sub(r'\s+', ' ', name)
        
        return name[:MaidInputValidator.MAX_NAME_LENGTH]

class MaidFuzzySearch:
    """Fuzzy search implementation cho maid system"""
    
    @staticmethod
    def search_maids(search_term: str, all_maids: Dict[str, Any], threshold: float = 0.6) -> List[Tuple[str, Dict, float]]:
        """
        Implement fuzzy search for maids
        
        Args:
            search_term: Từ khóa tìm kiếm
            all_maids: Dictionary tất cả maids
            threshold: Ngưỡng similarity minimum
            
        Returns:
            List[Tuple[str, Dict, float]]: List (maid_id, template, score)
        """
        search_lower = search_term.lower().strip()
        results = []
        
        for maid_id, template in all_maids.items():
            score = 0.0
            
            # Exact name match (highest priority)
            if search_lower == template["name"].lower():
                score = 1.0
            # Starts with search term
            elif template["name"].lower().startswith(search_lower):
                score = 0.95
            # Contains search term
            elif search_lower in template["name"].lower():
                score = 0.9
            # Full name matches
            elif search_lower in template["full_name"].lower():
                score = 0.85
            # Series matches
            elif "series" in template and search_lower in template["series"].lower():
                score = 0.8
            else:
                # Fuzzy matching
                name_ratio = difflib.SequenceMatcher(None, search_lower, template["name"].lower()).ratio()
                full_name_ratio = difflib.SequenceMatcher(None, search_lower, template["full_name"].lower()).ratio()
                score = max(name_ratio, full_name_ratio)
            
            if score >= threshold:
                results.append((maid_id, template, score))
        
        # Sort by score (highest first), then by name
        results.sort(key=lambda x: (-x[2], x[1]["name"]))
        return results
    
    @staticmethod
    def search_user_maids(search_term: str, user_maids: List, maid_templates: Dict[str, Any]) -> List:
        """
        Search trong collection của user với fuzzy matching
        
        Args:
            search_term: Từ khóa tìm kiếm
            user_maids: List UserMaid objects
            maid_templates: Dictionary maid templates
            
        Returns:
            List: Filtered user maids
        """
        search_lower = search_term.lower().strip()
        results = []
        
        for maid in user_maids:
            # Check instance ID
            if search_lower in maid.instance_id.lower():
                results.append((maid, 1.0))
                continue
            
            # Check custom name
            if maid.custom_name and search_lower in maid.custom_name.lower():
                results.append((maid, 0.95))
                continue
            
            # Check template name
            if maid.maid_id in maid_templates:
                template = maid_templates[maid.maid_id]
                if search_lower in template["name"].lower():
                    results.append((maid, 0.9))
                    continue
                    
                # Fuzzy match
                name_ratio = difflib.SequenceMatcher(None, search_lower, template["name"].lower()).ratio()
                if name_ratio >= 0.6:
                    results.append((maid, name_ratio))
        
        # Sort by score and return maids only
        results.sort(key=lambda x: -x[1])
        return [maid for maid, score in results]

# Global instances
maid_validator = MaidInputValidator()
maid_fuzzy_search = MaidFuzzySearch() 