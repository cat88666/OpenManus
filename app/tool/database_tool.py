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
from typing import Optional, Dict, Any, List, Union
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
       - data: 要插入或更新的数据（字典或字典列表）
    
    3. delete: 删除数据
       - table: 表名
       - where: WHERE条件
    
    4. execute: 执行自定义SQL
       - sql: 要执行的SQL语句
       - params: SQL参数（可选）
       
    5. get_table_schema: 获取表结构
       - table: 表名
    """
    
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "要执行的操作 (query, upsert, delete, execute, get_table_schema)"
            },
            "table": {
                "type": "string",
                "description": "表名"
            },
            "data": {
                "type": "object",
                "description": "要插入或更新的数据"
            },
            "where": {
                "type": "string",
                "description": "WHERE条件"
            },
            "limit": {
                "type": "integer",
                "description": "限制返回行数"
            },
            "order_by": {
                "type": "string",
                "description": "排序字段"
            },
            "sql": {
                "type": "string",
                "description": "要执行的SQL语句"
            },
            "params": {
                "type": "array",
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
            'ssl_ca': '/etc/ssl/certs/ca-certificates.crt',
            'ssl_verify_cert': False,
        }
    
    def _get_connection(self):
        """获取数据库连接"""
        try:
            conn = pymysql.connect(**self._db_config)
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
            with conn.cursor() as cursor:
                sql = f"SELECT * FROM `{table}`"
                if where:
                    sql += f" WHERE {where}"
                if order_by:
                    sql += f" ORDER BY {order_by}"
                if limit:
                    sql += f" LIMIT {limit}"
                
                cursor.execute(sql)
                result = cursor.fetchall()
                return self.success_response(result)
        except Exception as e:
            logger.error(f"查询失败: {str(e)}")
            return self.fail_response(f"查询失败: {str(e)}")
        finally:
            if conn:
                conn.close()

    async def _upsert(self, table: str, data: Union[Dict[str, Any], List[Dict[str, Any]]], **kwargs) -> ToolResult:
        """
        插入或更新数据
        
        Args:
            table: 表名
            data: 要插入或更新的数据（字典或字典列表）
        
        Returns:
            ToolResult: 操作结果
        """
        conn = None
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                if isinstance(data, dict):
                    data = [data]
                
                for item in data:
                    cols = ", ".join([f"`{k}`" for k in item.keys()])
                    vals = ", ".join([f"%s" for _ in item.values()])
                    updates = ", ".join([f"`{k}`=VALUES(`{k}`)" for k in item.keys()])
                    
                    # 将列表转换为JSON字符串
                    for key, value in item.items():
                        if isinstance(value, list):
                            item[key] = json.dumps(value)

                    cols = ", ".join([f"`{k}`" for k in item.keys()])
                    vals = ", ".join(["%s" for _ in item.values()])
                    updates = ", ".join([f"`{k}`=VALUES(`{k}`)" for k in item.keys()])
                    
                    sql = f"INSERT INTO `{table}` ({cols}) VALUES ({vals}) ON DUPLICATE KEY UPDATE {updates}"
                    cursor.execute(sql, tuple(item.values()))
            
            conn.commit()
            return self.success_response(f"成功插入/更新 {len(data)} 条记录")
        except Exception as e:
            logger.error(f"插入/更新失败: {str(e)}")
            if conn:
                conn.rollback()
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
            conn = self._get_connection()
            with conn.cursor() as cursor:
                sql = f"DELETE FROM `{table}` WHERE {where}"
                affected_rows = cursor.execute(sql)
            conn.commit()
            return self.success_response(f"成功删除 {affected_rows} 条记录")
        except Exception as e:
            logger.error(f"删除失败: {str(e)}")
            if conn:
                conn.rollback()
            return self.fail_response(f"删除失败: {str(e)}")
        finally:
            if conn:
                conn.close()

    async def _execute_sql(self, sql: str, params: Optional[List[Any]] = None, **kwargs) -> ToolResult:
        """
        执行自定义SQL
        
        Args:
            sql: 要执行的SQL语句
            params: SQL参数（可选）
        
        Returns:
            ToolResult: 操作结果
        """
        conn = None
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                result = cursor.fetchall()
            conn.commit()
            return self.success_response(result)
        except Exception as e:
            logger.error(f"SQL执行失败: {str(e)}")
            if conn:
                conn.rollback()
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
            with conn.cursor() as cursor:
                cursor.execute(f"DESCRIBE `{table}`")
                schema = cursor.fetchall()
                return self.success_response(schema)
        except Exception as e:
            logger.error(f"获取表结构失败: {str(e)}")
            return self.fail_response(f"获取表结构失败: {str(e)}")
        finally:
            if conn:
                conn.close()
