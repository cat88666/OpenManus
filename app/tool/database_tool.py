# -*- coding: utf-8 -*-
"""
MySQL数据库工具模块

让 Manus 具备读写 MySQL 的能力，使其不仅能"思考"，还能"记录"。
通过这个工具，Manus 可以：
1. 查询数据库中的数据（如查询待处理的机会）
2. 插入或更新数据（如保存爬取到的职位）
3. 删除数据（如标记已处理的任务）
"""

import json
import os
from typing import Optional, Dict, Any, List
from pydantic import Field
import pymysql
from pymysql.cursors import DictCursor

from app.tool.base import BaseTool, ToolResult
from app.utils.logger import logger


class DatabaseTool(BaseTool):
    """
    MySQL数据库工具
    
    提供对MySQL数据库的读写能力，让Manus能够：
    - 查询数据（SELECT）
    - 插入数据（INSERT）
    - 更新数据（UPDATE）
    - 删除数据（DELETE）
    - 执行自定义SQL
    """
    
    class Config:
        """Pydantic配置"""
        arbitrary_types_allowed = True
        underscore_attrs_are_private = False
    
    name: str = "database"
    description: str = """
    MySQL数据库工具，用于读写数据库。支持以下操作：
    
    1. query: 查询数据库中的数据
       - table: 表名
       - where: WHERE条件（可选）
       - limit: 限制返回行数（可选，默认10）
       - order_by: 排序字段（可选）
    
    2. upsert: 插入或更新数据
       - table: 表名
       - data: 要插入/更新的数据（字典）
       - where: 更新条件（可选，如果提供则更新，否则插入）
    
    3. delete: 删除数据
       - table: 表名
       - where: WHERE条件
    
    4. execute: 执行自定义SQL
       - sql: SQL语句
       - params: SQL参数（可选）
    
    5. get_table_schema: 获取表结构
       - table: 表名
    
    示例：
    - 查询待处理的机会：query(table='opportunities', where='status=1', limit=10)
    - 保存爬取的职位：upsert(table='opportunities', data={...})
    - 更新任务状态：upsert(table='tasks', data={'status': 2}, where='id=123')
    """
    
    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["query", "upsert", "delete", "execute", "get_table_schema"],
                "description": "要执行的操作类型"
            },
            "table": {
                "type": "string",
                "description": "表名"
            },
            "data": {
                "type": "object",
                "description": "要插入/更新的数据（字典格式）"
            },
            "where": {
                "type": "string",
                "description": "WHERE条件，如 'id=123' 或 'status=1 AND type=\"job\"'"
            },
            "limit": {
                "type": "integer",
                "description": "限制返回的行数，默认10"
            },
            "order_by": {
                "type": "string",
                "description": "排序字段，如 'created_at DESC'"
            },
            "sql": {
                "type": "string",
                "description": "自定义SQL语句"
            },
            "params": {
                "type": "object",
                "description": "SQL参数"
            }
        },
        "required": ["action"]
    }
    
    def __init__(self, **kwargs):
        """初始化数据库工具"""
        super().__init__(**kwargs)
        self._db_config = {
            'host': os.getenv('DB_HOST', 'mysql-df85ad2-facenada1107-6e0b.b.aivencloud.com'),
            'port': int(os.getenv('DB_PORT', '23808')),
            'user': os.getenv('DB_USER', 'avnadmin'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'defaultdb'),
            'charset': 'utf8mb4',
            'cursorclass': DictCursor,
            'ssl_verify_cert': True,
            'ssl_verify_identity': True,
            'ssl': True,
        }
    
    def _get_connection(self):
        """获取数据库连接"""
        try:
            # 为Aiven Cloud MySQL配置 SSL选项
            ssl_config = {
                'ca': '/etc/ssl/certs/ca-certificates.crt',
                'check_hostname': True,
                'verify_cert': True,
            }
            config = {**self._db_config}
            if config.get('ssl'):
                config['ssl'] = ssl_config
            conn = pymysql.connect(**config)
            return conn
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            raise
    
    async def execute(self, action: str, **kwargs) -> ToolResult:
        """
        执行数据库操作
        
        Args:
            action: 操作类型 (query, upsert, delete, execute, get_table_schema)
            **kwargs: 其他参数
        
        Returns:
            ToolResult: 操作结果
        """
        try:
            if action == "query":
                return await self._query(**kwargs)
            elif action == "upsert":
                return await self._upsert(**kwargs)
            elif action == "delete":
                return await self._delete(**kwargs)
            elif action == "execute":
                return await self._execute_sql(**kwargs)
            elif action == "get_table_schema":
                return await self._get_table_schema(**kwargs)
            else:
                return self.fail_response(f"未知的操作类型: {action}")
        except Exception as e:
            logger.error(f"数据库操作失败: {str(e)}")
            return self.fail_response(f"数据库操作失败: {str(e)}")
    
    async def _query(self, table: str, where: Optional[str] = None, 
                     limit: int = 10, order_by: Optional[str] = None, **kwargs) -> ToolResult:
        """
        查询数据库
        
        Args:
            table: 表名
            where: WHERE条件（可选）
            limit: 限制返回行数
            order_by: 排序字段（可选）
        
        Returns:
            ToolResult: 查询结果
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 构建SQL语句
            sql = f"SELECT * FROM {table}"
            
            if where:
                sql += f" WHERE {where}"
            
            if order_by:
                sql += f" ORDER BY {order_by}"
            
            sql += f" LIMIT {limit}"
            
            logger.debug(f"执行查询: {sql}")
            cursor.execute(sql)
            results = cursor.fetchall()
            
            # 统计信息
            count = len(results)
            
            return self.success_response({
                "table": table,
                "count": count,
                "data": results,
                "message": f"查询成功，返回 {count} 条记录"
            })
        
        except Exception as e:
            logger.error(f"查询失败: {str(e)}")
            return self.fail_response(f"查询失败: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    async def _upsert(self, table: str, data: Dict[str, Any], 
                      where: Optional[str] = None, **kwargs) -> ToolResult:
        """
        插入或更新数据
        
        Args:
            table: 表名
            data: 要插入/更新的数据
            where: 更新条件（如果提供则更新，否则插入）
        
        Returns:
            ToolResult: 操作结果
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if where:
                # 更新操作
                set_clause = ", ".join([f"`{k}`=%s" for k in data.keys()])
                sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
                values = list(data.values())
                
                logger.debug(f"执行更新: {sql}")
                cursor.execute(sql, values)
                affected_rows = cursor.rowcount
                
                conn.commit()
                
                return self.success_response({
                    "action": "update",
                    "table": table,
                    "affected_rows": affected_rows,
                    "message": f"更新成功，影响 {affected_rows} 行"
                })
            else:
                # 插入操作
                # 添加时间戳
                data['created_at'] = datetime.now().isoformat()
                data['updated_at'] = datetime.now().isoformat()
                
                columns = ", ".join([f"`{k}`" for k in data.keys()])
                placeholders = ", ".join(["%s"] * len(data))
                sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                values = list(data.values())
                
                logger.debug(f"执行插入: {sql}")
                cursor.execute(sql, values)
                inserted_id = cursor.lastrowid
                
                conn.commit()
                
                return self.success_response({
                    "action": "insert",
                    "table": table,
                    "inserted_id": inserted_id,
                    "message": f"插入成功，新记录ID: {inserted_id}"
                })
        
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"插入/更新失败: {str(e)}")
            return self.fail_response(f"插入/更新失败: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    async def _delete(self, table: str, where: str, **kwargs) -> ToolResult:
        """
        删除数据
        
        Args:
            table: 表名
            where: WHERE条件
        
        Returns:
            ToolResult: 操作结果
        """
        conn = None
        try:
            if not where:
                return self.fail_response("删除操作必须提供WHERE条件")
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            sql = f"DELETE FROM {table} WHERE {where}"
            
            logger.debug(f"执行删除: {sql}")
            cursor.execute(sql)
            affected_rows = cursor.rowcount
            
            conn.commit()
            
            return self.success_response({
                "action": "delete",
                "table": table,
                "affected_rows": affected_rows,
                "message": f"删除成功，删除 {affected_rows} 行"
            })
        
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"删除失败: {str(e)}")
            return self.fail_response(f"删除失败: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    async def _execute_sql(self, sql: str, params: Optional[Dict] = None, **kwargs) -> ToolResult:
        """
        执行自定义SQL
        
        Args:
            sql: SQL语句
            params: SQL参数（可选）
        
        Returns:
            ToolResult: 操作结果
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            logger.debug(f"执行自定义SQL: {sql}")
            
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            # 检查是否是SELECT语句
            if sql.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                conn.commit()
                return self.success_response({
                    "action": "select",
                    "count": len(results),
                    "data": results
                })
            else:
                affected_rows = cursor.rowcount
                conn.commit()
                return self.success_response({
                    "action": "execute",
                    "affected_rows": affected_rows,
                    "message": f"SQL执行成功，影响 {affected_rows} 行"
                })
        
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"SQL执行失败: {str(e)}")
            return self.fail_response(f"SQL执行失败: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    async def _get_table_schema(self, table: str, **kwargs) -> ToolResult:
        """
        获取表结构
        
        Args:
            table: 表名
        
        Returns:
            ToolResult: 表结构信息
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            sql = f"DESCRIBE {table}"
            
            logger.debug(f"获取表结构: {sql}")
            cursor.execute(sql)
            schema = cursor.fetchall()
            
            return self.success_response({
                "table": table,
                "schema": schema,
                "message": f"表 {table} 有 {len(schema)} 个字段"
            })
        
        except Exception as e:
            logger.error(f"获取表结构失败: {str(e)}")
            return self.fail_response(f"获取表结构失败: {str(e)}")
        finally:
            if conn:
                conn.close()


if __name__ == "__main__":
    import asyncio
    
    # 测试数据库工具
    tool = DatabaseTool()
    
    # 测试查询
    print("测试查询操作...")
    result = asyncio.run(tool.execute(
        action="query",
        table="opportunities",
        where="status=1",
        limit=5
    ))
    print(result)
