import sqlite3
import re
from typing import List, Dict
from utils.db_simulator import DB_PATH, get_structured_schema

class SchemaRAG:
    """Simple keyword-based RAG for database schema."""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.table_keywords = self._build_table_keywords()
        print(f"Schema RAG initialized with {len(self.table_keywords)} tables")
    
    def _build_table_keywords(self) -> Dict[str, List[str]]:
        """Build keyword mappings for each table."""
        return {
            'products': ['product', 'item', 'catalog', 'price', 'category', 'brand', 'sales', 'sold'],
            'product_variants': ['variant', 'product', 'sku', 'color', 'size', 'brand', 'sales', 'sold'],
            'customers': ['customer', 'user', 'client', 'buyer', 'person', 'email', 'name'],
            'orders': ['order', 'purchase', 'transaction', 'sale', 'buy', 'total', 'amount', 'sales'],
            'order_items': ['item', 'product', 'quantity', 'line', 'detail', 'sales', 'sold', 'brand'],
            'payments': ['payment', 'pay', 'money', 'revenue', 'amount'],
            'inventory': ['inventory', 'stock', 'quantity', 'warehouse', 'available'],
            'reviews': ['review', 'rating', 'feedback', 'comment', 'opinion'],
            'suppliers': ['supplier', 'vendor', 'procurement', 'purchase'],
            'categories': ['category', 'type', 'classification', 'group'],
            'brands': ['brand', 'manufacturer', 'company', 'sales', 'sold', 'quantity', 'total'],
            'addresses': ['address', 'location', 'shipping', 'billing'],
            'shipments': ['shipment', 'delivery', 'shipping', 'tracking'],
            'discounts': ['discount', 'coupon', 'promotion', 'offer'],
            'warehouses': ['warehouse', 'facility', 'location', 'storage'],
            'employees': ['employee', 'staff', 'worker', 'person'],
            'departments': ['department', 'division', 'team'],
            'product_images': ['image', 'photo', 'picture', 'media'],
            'purchase_orders': ['purchase', 'procurement', 'supplier', 'order'],
            'purchase_order_items': ['purchase', 'procurement', 'supplier', 'item'],
            'order_discounts': ['discount', 'coupon', 'promotion', 'order'],
            'shipment_items': ['shipment', 'delivery', 'item', 'tracking']
        }
    
    def get_relevant_schema(self, user_query: str, max_tables: int = 5) -> str:
        """Get relevant schema based on user query."""
        try:
            # Score tables by keyword relevance
            query_words = set(re.findall(r'\b\w+\b', user_query.lower()))
            table_scores = {}
            
            for table_name, keywords in self.table_keywords.items():
                score = 0
                
                # Count keyword matches
                for keyword in keywords:
                    if keyword in query_words:
                        score += 3
                    # Partial matches
                    for query_word in query_words:
                        if keyword in query_word or query_word in keyword:
                            score += 1
                
                # Bonus for exact table name match
                if table_name.lower() in query_words:
                    score += 10
                
                table_scores[table_name] = score
            
            # Get top scoring tables
            sorted_tables = sorted(table_scores.items(), key=lambda x: x[1], reverse=True)
            relevant_tables = [table for table, score in sorted_tables[:max_tables] if score > 0]
            
            # Fallback to default tables if no matches
            if not relevant_tables:
                relevant_tables = self._get_default_tables(user_query)[:max_tables]
            
            # Build schema for selected tables
            return self._build_schema(relevant_tables)
            
        except Exception as e:
            print(f"RAG error: {e}")
            return get_structured_schema(self.db_path)
    
    def _get_default_tables(self, user_query: str) -> List[str]:
        """Get default tables based on query patterns."""
        query_lower = user_query.lower()
        
        # Sales/revenue queries
        if any(word in query_lower for word in ['revenue', 'sales', 'total', 'amount', 'brand']):
            return ['orders', 'order_items', 'product_variants', 'products', 'brands']
        
        # Product queries
        if any(word in query_lower for word in ['product', 'item', 'catalog']):
            return ['products', 'product_variants', 'categories', 'brands']
        
        # Customer queries
        if any(word in query_lower for word in ['customer', 'user', 'buyer']):
            return ['customers', 'orders', 'addresses']
        
        # Default
        return ['products', 'customers', 'orders', 'order_items']
    
    def _build_schema(self, table_names: List[str]) -> str:
        """Build schema string for specified tables."""
        if not table_names:
            return get_structured_schema(self.db_path)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        schema_lines = ["Available tables and columns:"]
        
        try:
            for table_name in table_names:
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                if columns:
                    col_names = [col[1] for col in columns]
                    schema_lines.append(f"- {table_name}: {', '.join(col_names)}")
        finally:
            conn.close()
        
        return '\n'.join(schema_lines)


# Convenience functions
def get_rag_enhanced_schema(user_query: str, db_path: str = DB_PATH) -> str:
    """Get RAG-enhanced schema for a user query."""
    try:
        schema_rag = SchemaRAG(db_path)
        return schema_rag.get_relevant_schema(user_query)
    except Exception as e:
        print(f"RAG failed: {e}")
        return get_structured_schema(db_path)


# Global cached instance
_schema_rag_instance = None

def get_cached_schema_rag(db_path: str = DB_PATH) -> SchemaRAG:
    """Get cached SchemaRAG instance."""
    global _schema_rag_instance
    if _schema_rag_instance is None:
        _schema_rag_instance = SchemaRAG(db_path)
    return _schema_rag_instance