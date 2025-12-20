#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGPT Conversation Viewer - Flask Web Application
"""

from flask import Flask, render_template, request, redirect, url_for, abort, jsonify, make_response, send_file
import sqlite3
import markdown
from datetime import datetime, timedelta
import os
import io
from urllib.parse import quote
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

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


@app.route('/api/contribution_data')
def contribution_data():
    """
    API endpoint: Return daily conversation counts for the past year
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Get data for the past 365 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    cursor.execute('''
        SELECT DATE(create_time) as date, COUNT(*) as count
        FROM conversations
        WHERE create_time >= ? AND create_time <= ?
        GROUP BY DATE(create_time)
        ORDER BY date ASC
    ''', (start_date, end_date))
    
    results = cursor.fetchall()
    conn.close()
    
    # Convert to dictionary format
    data = {}
    for row in results:
        data[row[0]] = row[1]
    
    return jsonify(data)


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


@app.route('/export/<conversation_id>/markdown')
def export_markdown(conversation_id):
    """
    Export conversation as Markdown file
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
    
    # Generate Markdown content
    md_content = []
    md_content.append(f"# {conversation['title'] or '無標題對話'}\n")
    md_content.append(f"**建立時間**: {conversation['create_time']}\n")
    
    if conversation['tags']:
        md_content.append(f"**標籤**: {conversation['tags']}\n")
    
    md_content.append(f"**訊息數量**: {len(messages)}\n")
    md_content.append(f"**字元數**: {conversation['total_char_count'] or 0}\n")
    md_content.append("\n---\n\n")
    
    # Add messages
    for message in messages:
        role_name = "👤 使用者" if message['role'] == 'user' else "🤖 ChatGPT"
        md_content.append(f"## {role_name}\n")
        md_content.append(f"*時間: {message['create_time']}*\n\n")
        md_content.append(f"{message['content']}\n\n")
        md_content.append("---\n\n")
    
    # Create response
    response = make_response('\n'.join(md_content))
    response.headers['Content-Type'] = 'text/markdown; charset=utf-8'
    
    # Safe filename - use only ASCII characters or encode properly
    safe_title = "".join(c for c in (conversation['title'] or 'conversation') if c.isalnum() or c in (' ', '-', '_')).strip()
    if not safe_title or not safe_title.replace(' ', '').replace('-', '').replace('_', ''):
        safe_title = "conversation"
    safe_title = safe_title[:50]  # Limit length
    filename = f"{safe_title}_{conversation_id[:8]}.md"
    
    # Use RFC 5987 encoding for non-ASCII filenames
    try:
        filename.encode('ascii')
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    except UnicodeEncodeError:
        # Fallback to ASCII-only filename with UTF-8 encoded alternative
        ascii_filename = f"conversation_{conversation_id[:8]}.md"
        encoded_filename = quote(filename)
        response.headers['Content-Disposition'] = f"attachment; filename=\"{ascii_filename}\"; filename*=UTF-8''{encoded_filename}"
    
    return response


@app.route('/export/<conversation_id>/pdf')
def export_pdf(conversation_id):
    """
    Export conversation as PDF file
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
    
    # Create PDF in memory
    buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Register CJK font for Chinese characters
    try:
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
        font_name = 'STSong-Light'
    except:
        # Fallback to default font if CJK font not available
        font_name = 'Helvetica'
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        fontName=font_name,
        spaceAfter=12,
        alignment=TA_LEFT
    )
    
    # Metadata style
    meta_style = ParagraphStyle(
        'CustomMeta',
        parent=styles['Normal'],
        fontSize=10,
        fontName=font_name,
        spaceAfter=6,
        textColor='grey'
    )
    
    # Message header style
    msg_header_style = ParagraphStyle(
        'MessageHeader',
        parent=styles['Heading2'],
        fontSize=12,
        fontName=font_name,
        spaceAfter=6,
        spaceBefore=12
    )
    
    # Message content style
    msg_content_style = ParagraphStyle(
        'MessageContent',
        parent=styles['Normal'],
        fontSize=10,
        fontName=font_name,
        spaceAfter=12,
        leftIndent=20
    )
    
    # Add title
    title = Paragraph(conversation['title'] or '無標題對話', title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Add metadata
    meta_lines = [
        f"建立時間: {conversation['create_time']}",
        f"訊息數量: {len(messages)}",
        f"字元數: {conversation['total_char_count'] or 0}"
    ]
    
    if conversation['tags']:
        meta_lines.append(f"標籤: {conversation['tags']}")
    
    for line in meta_lines:
        elements.append(Paragraph(line, meta_style))
    
    elements.append(Spacer(1, 24))
    
    # Add messages
    for message in messages:
        role_name = "使用者" if message['role'] == 'user' else "ChatGPT"
        
        # Message header
        header_text = f"{role_name} - {message['create_time']}"
        elements.append(Paragraph(header_text, msg_header_style))
        
        # Message content (escape HTML special characters and handle long text)
        content = message['content'] or ""
        # Replace special characters that might cause issues
        content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # Limit content length to avoid very long pages
        if len(content) > 5000:
            content = content[:5000] + "...(內容過長，已截斷)"
        
        try:
            elements.append(Paragraph(content, msg_content_style))
        except Exception as e:
            # If content causes issues, use a simplified version
            elements.append(Paragraph("[內容無法正確顯示]", msg_content_style))
        
        elements.append(Spacer(1, 12))
    
    # Build PDF
    try:
        doc.build(elements)
    except Exception as e:
        # If PDF generation fails, return an error
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500
    
    buffer.seek(0)
    
    # Safe filename - use only ASCII characters or encode properly
    safe_title = "".join(c for c in (conversation['title'] or 'conversation') if c.isalnum() or c in (' ', '-', '_')).strip()
    if not safe_title or not safe_title.replace(' ', '').replace('-', '').replace('_', ''):
        safe_title = "conversation"
    safe_title = safe_title[:50]  # Limit length
    filename = f"{safe_title}_{conversation_id[:8]}.pdf"
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )


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
