#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETL Script for ChatGPT Conversation History
Parses large JSON files using streaming with ijson to avoid memory issues
"""

import sqlite3
import ijson
from datetime import datetime
import sys
import os


def create_database(db_path='chat_history.db'):
    """
    Create SQLite database with conversations and messages tables
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create conversations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT,
            create_time DATETIME,
            tags TEXT,
            total_char_count INTEGER
        )
    ''')
    
    # Create messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT,
            role TEXT,
            content TEXT,
            create_time DATETIME,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    ''')
    
    # Create indexes for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_conv_create_time 
        ON conversations(create_time DESC)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_msg_conversation_id 
        ON messages(conversation_id)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_msg_create_time 
        ON messages(create_time)
    ''')
    
    # Full-text search for messages
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts 
        USING fts5(message_id, content, content=messages, content_rowid=rowid)
    ''')
    
    conn.commit()
    conn.close()
    print(f"✓ Database created: {db_path}")


def extract_message_content(message_data):
    """
    Extract text content from a message's content structure
    """
    if not message_data:
        return ""
    
    content = message_data.get('content')
    if not content:
        return ""
    
    # Handle different content structures
    if isinstance(content, str):
        return content
    
    if isinstance(content, dict):
        parts = content.get('parts', [])
        if isinstance(parts, list):
            # Concatenate all parts
            return ' '.join(str(part) for part in parts if part)
        return str(content)
    
    return str(content)


def generate_tags(title):
    """
    Generate tags based on conversation title
    """
    tags = []
    title_lower = title.lower() if title else ""
    
    # Simple rule-based tagging
    if any(keyword in title_lower for keyword in ['python', 'code', 'programming', '程式', '編程', 'script']):
        tags.append('Coding')
    
    if any(keyword in title_lower for keyword in ['data', 'database', 'sql', '資料']):
        tags.append('Data')
    
    if any(keyword in title_lower for keyword in ['web', 'html', 'css', 'javascript', 'flask', 'django']):
        tags.append('Web Development')
    
    if any(keyword in title_lower for keyword in ['ai', 'ml', 'machine learning', 'deep learning', '機器學習']):
        tags.append('AI/ML')
    
    return ', '.join(tags) if tags else ''


def parse_and_insert(json_path='conversations.json', db_path='chat_history.db', batch_size=1000):
    """
    Parse JSON file using streaming and insert into SQLite database
    Uses ijson to avoid loading entire file into memory
    """
    if not os.path.exists(json_path):
        print(f"✗ Error: File not found: {json_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    conv_batch = []
    msg_batch = []
    
    total_conversations = 0
    total_messages = 0
    
    print(f"📖 Parsing {json_path} using streaming...")
    print(f"   File size: {os.path.getsize(json_path) / 1024 / 1024:.2f} MB")
    
    try:
        with open(json_path, 'rb') as f:
            # Stream through each conversation item
            # Check if JSON is array or object
            # Use 'item' for arrays at root level
            parser = ijson.items(f, 'item')
            
            for conv in parser:
                try:
                    # Extract conversation metadata
                    conv_id = conv.get('id') or conv.get('conversation_id')
                    if not conv_id:
                        continue
                    
                    title = conv.get('title', 'Untitled')
                    create_time_unix = conv.get('create_time', 0)
                    # Convert Decimal to float if needed
                    if create_time_unix:
                        create_time_unix = float(create_time_unix)
                        create_time = datetime.fromtimestamp(create_time_unix)
                    else:
                        create_time = datetime.now()
                    
                    # Generate tags
                    tags = generate_tags(title)
                    
                    # Extract messages from mapping
                    mapping = conv.get('mapping', {})
                    conversation_messages = []
                    total_chars = 0
                    
                    for node_id, node_data in mapping.items():
                        if not node_data or not isinstance(node_data, dict):
                            continue
                        
                        message = node_data.get('message')
                        if not message:
                            continue
                        
                        # Extract role
                        author = message.get('author', {})
                        role = author.get('role') if isinstance(author, dict) else None
                        
                        # Only keep user and assistant messages
                        if role not in ['user', 'assistant']:
                            continue
                        
                        # Extract content
                        content = extract_message_content(message)
                        if not content or content.strip() == '':
                            continue
                        
                        # Get message creation time
                        msg_create_time_unix = message.get('create_time', create_time_unix)
                        if msg_create_time_unix:
                            msg_create_time = datetime.fromtimestamp(float(msg_create_time_unix))
                        else:
                            msg_create_time = create_time
                        
                        # Get message ID
                        msg_id = message.get('id', f"{conv_id}_{node_id}")
                        
                        conversation_messages.append({
                            'id': msg_id,
                            'conversation_id': conv_id,
                            'role': role,
                            'content': content,
                            'create_time': msg_create_time
                        })
                        
                        total_chars += len(content)
                    
                    # Add conversation to batch
                    conv_batch.append((
                        conv_id,
                        title,
                        create_time,
                        tags,
                        total_chars
                    ))
                    
                    # Add messages to batch
                    msg_batch.extend(conversation_messages)
                    
                    total_conversations += 1
                    total_messages += len(conversation_messages)
                    
                    # Commit in batches to balance memory and I/O
                    if len(conv_batch) >= batch_size:
                        # Insert conversations
                        cursor.executemany(
                            'INSERT OR REPLACE INTO conversations VALUES (?, ?, ?, ?, ?)',
                            conv_batch
                        )
                        
                        # Insert messages
                        for msg in msg_batch:
                            cursor.execute(
                                'INSERT OR REPLACE INTO messages VALUES (?, ?, ?, ?, ?)',
                                (msg['id'], msg['conversation_id'], msg['role'], 
                                 msg['content'], msg['create_time'])
                            )
                        
                        conn.commit()
                        print(f"   ✓ Processed {total_conversations} conversations, {total_messages} messages...")
                        
                        conv_batch = []
                        msg_batch = []
                
                except Exception as e:
                    print(f"   ⚠ Warning: Error processing conversation: {e}")
                    continue
        
        # Insert remaining batch
        if conv_batch:
            cursor.executemany(
                'INSERT OR REPLACE INTO conversations VALUES (?, ?, ?, ?, ?)',
                conv_batch
            )
            
            for msg in msg_batch:
                cursor.execute(
                    'INSERT OR REPLACE INTO messages VALUES (?, ?, ?, ?, ?)',
                    (msg['id'], msg['conversation_id'], msg['role'], 
                     msg['content'], msg['create_time'])
                )
            
            conn.commit()
        
        # Update FTS index
        print("📝 Building full-text search index...")
        cursor.execute('''
            INSERT INTO messages_fts(message_id, content)
            SELECT id, content FROM messages
        ''')
        conn.commit()
        
        print(f"\n✅ Import completed successfully!")
        print(f"   Total conversations: {total_conversations}")
        print(f"   Total messages: {total_messages}")
        
    except Exception as e:
        print(f"✗ Error during parsing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


def main():
    """
    Main entry point for ETL script
    """
    print("=" * 60)
    print("ChatGPT Conversation History - ETL Script")
    print("=" * 60)
    
    # Get JSON file path from command line or use default
    json_path = sys.argv[1] if len(sys.argv) > 1 else 'conversations.json'
    db_path = sys.argv[2] if len(sys.argv) > 2 else 'chat_history.db'
    
    # Create database
    create_database(db_path)
    
    # Parse and insert data
    parse_and_insert(json_path, db_path)
    
    print("=" * 60)


if __name__ == '__main__':
    main()
