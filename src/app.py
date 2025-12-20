#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGPT Conversation Viewer - Flask Web Application
"""

from flask import Flask, render_template, request, redirect, url_for, abort
import sqlite3
import markdown
from datetime import datetime
import os

app = Flask(__name__)
# Change this to a random secret key in production
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')

# Database configuration
DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'chat_history.db')
ITEMS_PER_PAGE = 20


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.template_filter('markdown')
def markdown_filter(text):
    """
    Convert Markdown text to HTML
    Supports code blocks, lists, and other markdown features
    """
    if not text:
        return ""
    
    # Configure markdown with extensions
    md = markdown.Markdown(extensions=[
        'fenced_code',
        'codehilite',
        'tables',
        'nl2br'
    ])
    
    return md.convert(text)


@app.template_filter('datetime')
def datetime_filter(value):
    """Format datetime for display"""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except:
            return value
    
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M')
    
    return value


@app.route('/')
def index():
    """
    Main page: List conversations with search and pagination
    """
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    query = request.args.get('q', '').strip()
    
    # Calculate offset
    offset = (page - 1) * ITEMS_PER_PAGE
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Build query based on search
    if query:
        # Count total for pagination first
        search_pattern = f'%{query}%'
        count_sql = '''
            SELECT COUNT(DISTINCT c.id)
            FROM conversations c
            LEFT JOIN messages m ON c.id = m.conversation_id
            WHERE c.title LIKE ? OR m.content LIKE ?
        '''
        cursor.execute(count_sql, (search_pattern, search_pattern))
        total_count = cursor.fetchone()[0]
        
        # Search in title AND message content
        search_sql = '''
            SELECT DISTINCT c.id, c.title, c.create_time, c.tags, c.total_char_count
            FROM conversations c
            LEFT JOIN messages m ON c.id = m.conversation_id
            WHERE c.title LIKE ? OR m.content LIKE ?
            ORDER BY c.create_time DESC
            LIMIT ? OFFSET ?
        '''
        cursor.execute(search_sql, (search_pattern, search_pattern, ITEMS_PER_PAGE, offset))
        conversations = cursor.fetchall()
    else:
        # Count total first
        cursor.execute('SELECT COUNT(*) FROM conversations')
        total_count = cursor.fetchone()[0]
        
        # No search, just list all
        cursor.execute('''
            SELECT id, title, create_time, tags, total_char_count
            FROM conversations
            ORDER BY create_time DESC
            LIMIT ? OFFSET ?
        ''', (ITEMS_PER_PAGE, offset))
        conversations = cursor.fetchall()
    
    conn.close()
    
    # Calculate pagination
    total_pages = (total_count + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    return render_template('index.html',
                         conversations=conversations,
                         page=page,
                         total_pages=total_pages,
                         query=query,
                         total_count=total_count)


@app.route('/chat/<conversation_id>')
def chat_detail(conversation_id):
    """
    Detail page: Show full conversation with all messages
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Get conversation details
    cursor.execute('''
        SELECT id, title, create_time, tags, total_char_count
        FROM conversations
        WHERE id = ?
    ''', (conversation_id,))
    
    conversation = cursor.fetchone()
    
    if not conversation:
        conn.close()
        abort(404)
    
    # Get all messages for this conversation
    cursor.execute('''
        SELECT id, role, content, create_time
        FROM messages
        WHERE conversation_id = ?
        ORDER BY create_time ASC
    ''', (conversation_id,))
    
    messages = cursor.fetchall()
    
    conn.close()
    
    return render_template('detail.html',
                         conversation=conversation,
                         messages=messages)


@app.route('/stats')
def stats():
    """
    Statistics page: Show overview of conversation data
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Total conversations
    cursor.execute('SELECT COUNT(*) FROM conversations')
    total_conversations = cursor.fetchone()[0]
    
    # Total messages
    cursor.execute('SELECT COUNT(*) FROM messages')
    total_messages = cursor.fetchone()[0]
    
    # Average messages per conversation
    avg_messages = total_messages / total_conversations if total_conversations > 0 else 0
    
    # Most active month
    cursor.execute('''
        SELECT strftime('%Y-%m', create_time) as month, COUNT(*) as count
        FROM conversations
        GROUP BY month
        ORDER BY count DESC
        LIMIT 1
    ''')
    most_active_month = cursor.fetchone()
    
    # Tag distribution
    cursor.execute('''
        SELECT tags, COUNT(*) as count
        FROM conversations
        WHERE tags != ''
        GROUP BY tags
        ORDER BY count DESC
        LIMIT 10
    ''')
    tag_stats = cursor.fetchall()
    
    conn.close()
    
    return render_template('stats.html',
                         total_conversations=total_conversations,
                         total_messages=total_messages,
                         avg_messages=avg_messages,
                         most_active_month=most_active_month,
                         tag_stats=tag_stats)


@app.errorhandler(404)
def page_not_found(e):
    """404 error handler"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """500 error handler"""
    return render_template('500.html'), 500


if __name__ == '__main__':
    import os
    
    # Check if database exists
    if not os.path.exists(DATABASE):
        print("=" * 60)
        print("⚠️  WARNING: Database not found!")
        print("=" * 60)
        print(f"Please run etl_script.py first to create the database:")
        print(f"  python etl_script.py conversations.json")
        print("=" * 60)
    else:
        print("=" * 60)
        print("🚀 ChatGPT Conversation Viewer")
        print("=" * 60)
        print(f"📊 Database: {DATABASE}")
        print(f"🌐 Starting Flask server...")
        print("=" * 60)
    
    app.run(debug=True, host='127.0.0.1', port=5000)
