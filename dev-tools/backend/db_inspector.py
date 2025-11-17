#!/usr/bin/env python3
"""
Database Inspector
==================
Flask web UI for browsing and inspecting the ChromaDB vector database.

Usage:
    python dev-tools/backend/db_inspector.py

Access at: http://localhost:5001/

Features:
- Browse all chunks in the database
- Search chunks by text content
- Filter by chapter and section metadata
- View full chunk content with metadata
- Export database to CSV/JSON
- Delete individual chunks or entire collections
- Rebuild vector index
- View database statistics
"""

import sys
import csv
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from flask import Flask, render_template_string, request, jsonify, send_file
from src.vector_store import VectorStore

app = Flask(__name__)

# Global vector store instance
vector_store: Optional[VectorStore] = None


def get_vector_store():
    """Get or initialize the vector store."""
    global vector_store
    if vector_store is None:
        db_path = Path(__file__).parent.parent.parent / "backend" / "data" / "chroma_db"
        vector_store = VectorStore(persist_directory=str(db_path))
    return vector_store


# HTML Templates
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Inspector - Icelandic Chemistry AI</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f7fa;
            color: #2c3e50;
            line-height: 1.6;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }

        .stat-label {
            color: #7f8c8d;
            margin-top: 5px;
        }

        .controls {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .control-group {
            margin-bottom: 15px;
        }

        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #2c3e50;
        }

        input, select, button {
            font-size: 14px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }

        input[type="text"] {
            width: 100%;
        }

        select {
            min-width: 200px;
        }

        button {
            background: #667eea;
            color: white;
            border: none;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.3s;
        }

        button:hover {
            background: #5568d3;
        }

        button.danger {
            background: #e74c3c;
        }

        button.danger:hover {
            background: #c0392b;
        }

        button.success {
            background: #2ecc71;
        }

        button.success:hover {
            background: #27ae60;
        }

        .filter-row {
            display: grid;
            grid-template-columns: 3fr 1fr 1fr;
            gap: 10px;
            align-items: end;
        }

        .results {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .results-header {
            padding: 20px;
            border-bottom: 1px solid #ecf0f1;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .results-count {
            font-weight: 600;
            color: #7f8c8d;
        }

        .export-buttons button {
            margin-left: 10px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        thead {
            background: #f8f9fa;
        }

        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }

        th {
            font-weight: 600;
            color: #2c3e50;
        }

        tr:hover {
            background: #f8f9fa;
        }

        .chunk-preview {
            max-width: 400px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .view-btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
        }

        .view-btn:hover {
            background: #2980b9;
        }

        .delete-btn {
            background: #e74c3c;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
            margin-left: 5px;
        }

        .delete-btn:hover {
            background: #c0392b;
        }

        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
        }

        .modal-content {
            background: white;
            margin: 50px auto;
            padding: 30px;
            width: 90%;
            max-width: 800px;
            border-radius: 8px;
            max-height: 80vh;
            overflow-y: auto;
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
        }

        .close {
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            color: #7f8c8d;
        }

        .close:hover {
            color: #2c3e50;
        }

        .metadata {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
        }

        .metadata-item {
            margin-bottom: 10px;
        }

        .metadata-label {
            font-weight: 600;
            color: #7f8c8d;
            margin-right: 10px;
        }

        .chunk-text {
            line-height: 1.8;
            white-space: pre-wrap;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
        }

        .no-results {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Database Inspector</h1>
            <p>Icelandic Chemistry AI - Vector Database Browser</p>
        </header>

        <div class="stats" id="stats">
            <div class="stat-card">
                <div class="stat-value" id="totalChunks">-</div>
                <div class="stat-label">Total Chunks</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="totalChapters">-</div>
                <div class="stat-label">Unique Chapters</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="totalSections">-</div>
                <div class="stat-label">Unique Sections</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="totalWords">-</div>
                <div class="stat-label">Total Words</div>
            </div>
        </div>

        <div class="controls">
            <div class="filter-row">
                <div class="control-group">
                    <label>Search Text</label>
                    <input type="text" id="searchQuery" placeholder="Search chunks by content...">
                </div>
                <div class="control-group">
                    <label>Chapter</label>
                    <select id="chapterFilter">
                        <option value="">All Chapters</option>
                    </select>
                </div>
                <div class="control-group">
                    <label>Section</label>
                    <select id="sectionFilter">
                        <option value="">All Sections</option>
                    </select>
                </div>
            </div>
            <div style="margin-top: 15px;">
                <button onclick="searchChunks()">🔍 Search</button>
                <button onclick="loadAllChunks()" class="success">📋 Browse All</button>
                <button onclick="refreshStats()" class="success">🔄 Refresh Stats</button>
            </div>
        </div>

        <div class="results">
            <div class="results-header">
                <div class="results-count" id="resultsCount">No results</div>
                <div class="export-buttons">
                    <button onclick="exportCSV()" class="success">Export CSV</button>
                    <button onclick="exportJSON()" class="success">Export JSON</button>
                </div>
            </div>
            <div id="resultsTable">
                <div class="loading">Load data to view results</div>
            </div>
        </div>
    </div>

    <!-- Modal for viewing chunk details -->
    <div id="chunkModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Chunk Details</h2>
                <span class="close" onclick="closeModal()">&times;</span>
            </div>
            <div id="modalContent"></div>
        </div>
    </div>

    <script>
        let currentData = [];

        // Load stats on page load
        window.onload = function() {
            refreshStats();
            loadFilters();
        };

        async function refreshStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                document.getElementById('totalChunks').textContent = stats.total_chunks || 0;
                document.getElementById('totalChapters').textContent = stats.unique_chapters || 0;
                document.getElementById('totalSections').textContent = stats.unique_sections || 0;
                document.getElementById('totalWords').textContent = (stats.total_words || 0).toLocaleString();
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        async function loadFilters() {
            try {
                const response = await fetch('/api/filters');
                const filters = await response.json();

                const chapterSelect = document.getElementById('chapterFilter');
                filters.chapters.forEach(chapter => {
                    const option = document.createElement('option');
                    option.value = chapter;
                    option.textContent = `Chapter ${chapter}`;
                    chapterSelect.appendChild(option);
                });

                const sectionSelect = document.getElementById('sectionFilter');
                filters.sections.forEach(section => {
                    const option = document.createElement('option');
                    option.value = section;
                    option.textContent = `Section ${section}`;
                    sectionSelect.appendChild(option);
                });
            } catch (error) {
                console.error('Error loading filters:', error);
            }
        }

        async function searchChunks() {
            const query = document.getElementById('searchQuery').value;
            const chapter = document.getElementById('chapterFilter').value;
            const section = document.getElementById('sectionFilter').value;

            document.getElementById('resultsTable').innerHTML = '<div class="loading">Searching...</div>';

            try {
                const params = new URLSearchParams();
                if (query) params.append('query', query);
                if (chapter) params.append('chapter', chapter);
                if (section) params.append('section', section);

                const response = await fetch(`/api/search?${params}`);
                currentData = await response.json();
                displayResults(currentData);
            } catch (error) {
                console.error('Error searching:', error);
                document.getElementById('resultsTable').innerHTML = '<div class="no-results">Error loading results</div>';
            }
        }

        async function loadAllChunks() {
            document.getElementById('resultsTable').innerHTML = '<div class="loading">Loading all chunks...</div>';

            try {
                const response = await fetch('/api/chunks');
                currentData = await response.json();
                displayResults(currentData);
            } catch (error) {
                console.error('Error loading chunks:', error);
                document.getElementById('resultsTable').innerHTML = '<div class="no-results">Error loading results</div>';
            }
        }

        function displayResults(data) {
            const resultsCount = document.getElementById('resultsCount');
            const resultsTable = document.getElementById('resultsTable');

            if (!data || data.length === 0) {
                resultsCount.textContent = 'No results';
                resultsTable.innerHTML = '<div class="no-results">No chunks found</div>';
                return;
            }

            resultsCount.textContent = `${data.length} result(s)`;

            let html = '<table><thead><tr>';
            html += '<th>ID</th>';
            html += '<th>Chapter</th>';
            html += '<th>Section</th>';
            html += '<th>Title</th>';
            html += '<th>Words</th>';
            html += '<th>Preview</th>';
            html += '<th>Actions</th>';
            html += '</tr></thead><tbody>';

            data.forEach((chunk, index) => {
                html += '<tr>';
                html += `<td>${chunk.id}</td>`;
                html += `<td>${chunk.metadata.chapter || 'N/A'}</td>`;
                html += `<td>${chunk.metadata.section || 'N/A'}</td>`;
                html += `<td>${chunk.metadata.title || 'N/A'}</td>`;
                html += `<td>${chunk.metadata.word_count || 0}</td>`;
                html += `<td class="chunk-preview">${chunk.document.substring(0, 100)}...</td>`;
                html += `<td>
                    <button class="view-btn" onclick="viewChunk(${index})">View</button>
                    <button class="delete-btn" onclick="deleteChunk('${chunk.id}')">Delete</button>
                </td>`;
                html += '</tr>';
            });

            html += '</tbody></table>';
            resultsTable.innerHTML = html;
        }

        function viewChunk(index) {
            const chunk = currentData[index];
            const modal = document.getElementById('chunkModal');
            const content = document.getElementById('modalContent');

            let html = '<div class="metadata">';
            html += `<div class="metadata-item"><span class="metadata-label">ID:</span>${chunk.id}</div>`;
            html += `<div class="metadata-item"><span class="metadata-label">Chapter:</span>${chunk.metadata.chapter || 'N/A'}</div>`;
            html += `<div class="metadata-item"><span class="metadata-label">Section:</span>${chunk.metadata.section || 'N/A'}</div>`;
            html += `<div class="metadata-item"><span class="metadata-label">Title:</span>${chunk.metadata.title || 'N/A'}</div>`;
            html += `<div class="metadata-item"><span class="metadata-label">Word Count:</span>${chunk.metadata.word_count || 0}</div>`;
            if (chunk.metadata.filename) {
                html += `<div class="metadata-item"><span class="metadata-label">Filename:</span>${chunk.metadata.filename}</div>`;
            }
            html += '</div>';

            html += '<h3>Full Text</h3>';
            html += `<div class="chunk-text">${chunk.document}</div>`;

            content.innerHTML = html;
            modal.style.display = 'block';
        }

        function closeModal() {
            document.getElementById('chunkModal').style.display = 'none';
        }

        async function deleteChunk(chunkId) {
            if (!confirm(`Are you sure you want to delete chunk "${chunkId}"?`)) {
                return;
            }

            try {
                const response = await fetch(`/api/chunks/${chunkId}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    alert('Chunk deleted successfully');
                    refreshStats();
                    // Reload current view
                    if (currentData.length > 0) {
                        searchChunks();
                    }
                } else {
                    alert('Error deleting chunk');
                }
            } catch (error) {
                console.error('Error deleting chunk:', error);
                alert('Error deleting chunk');
            }
        }

        function exportCSV() {
            window.location.href = '/api/export/csv';
        }

        function exportJSON() {
            window.location.href = '/api/export/json';
        }

        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('chunkModal');
            if (event.target == modal) {
                closeModal();
            }
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Serve the main page."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/stats')
def get_stats():
    """Get database statistics."""
    try:
        vs = get_vector_store()
        stats = vs.get_stats()

        # Calculate total words
        all_docs = vs.get_all_documents()
        total_words = sum(meta.get('word_count', 0) for meta in all_docs['metadatas'][0])

        return jsonify({
            'total_chunks': stats['total_chunks'],
            'unique_chapters': stats['unique_chapters'],
            'unique_sections': stats['unique_sections'],
            'total_words': total_words
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/filters')
def get_filters():
    """Get available filter values."""
    try:
        vs = get_vector_store()
        stats = vs.get_stats()

        # Get unique sections
        all_docs = vs.get_all_documents()
        sections = sorted(set(meta.get('section', '') for meta in all_docs['metadatas'][0] if meta.get('section')))

        return jsonify({
            'chapters': sorted(stats.get('chapters', [])),
            'sections': sections
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chunks')
def get_all_chunks():
    """Get all chunks."""
    try:
        vs = get_vector_store()
        result = vs.get_all_documents()

        chunks = []
        for i, (doc_id, doc, meta) in enumerate(zip(
            result['ids'][0],
            result['documents'][0],
            result['metadatas'][0]
        )):
            chunks.append({
                'id': doc_id,
                'document': doc,
                'metadata': meta
            })

        return jsonify(chunks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search')
def search_chunks():
    """Search chunks with filters."""
    try:
        vs = get_vector_store()

        query = request.args.get('query', '').strip()
        chapter = request.args.get('chapter', '').strip()
        section = request.args.get('section', '').strip()

        # Build metadata filter
        where = {}
        if chapter:
            where['chapter'] = chapter
        if section:
            where['section'] = section

        # If text query provided, do semantic search
        if query:
            result = vs.search(
                query=query,
                n_results=50,
                where=where if where else None
            )

            chunks = []
            for i, (doc_id, doc, meta) in enumerate(zip(
                result['ids'][0],
                result['documents'][0],
                result['metadatas'][0]
            )):
                chunks.append({
                    'id': doc_id,
                    'document': doc,
                    'metadata': meta
                })

            return jsonify(chunks)

        # Otherwise, filter by metadata only
        else:
            all_docs = vs.get_all_documents()
            chunks = []

            for i, (doc_id, doc, meta) in enumerate(zip(
                all_docs['ids'][0],
                all_docs['documents'][0],
                all_docs['metadatas'][0]
            )):
                # Apply filters
                if chapter and meta.get('chapter') != chapter:
                    continue
                if section and meta.get('section') != section:
                    continue

                chunks.append({
                    'id': doc_id,
                    'document': doc,
                    'metadata': meta
                })

            return jsonify(chunks)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chunks/<chunk_id>', methods=['DELETE'])
def delete_chunk(chunk_id):
    """Delete a specific chunk."""
    try:
        vs = get_vector_store()
        vs.collection.delete(ids=[chunk_id])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/csv')
def export_csv():
    """Export database to CSV."""
    try:
        vs = get_vector_store()
        result = vs.get_all_documents()

        # Create CSV file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"db_export_{timestamp}.csv"
        filepath = Path("/tmp") / filename

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'chapter', 'section', 'title', 'word_count', 'document']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for doc_id, doc, meta in zip(
                result['ids'][0],
                result['documents'][0],
                result['metadatas'][0]
            ):
                writer.writerow({
                    'id': doc_id,
                    'chapter': meta.get('chapter', ''),
                    'section': meta.get('section', ''),
                    'title': meta.get('title', ''),
                    'word_count': meta.get('word_count', 0),
                    'document': doc
                })

        return send_file(str(filepath), as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/json')
def export_json():
    """Export database to JSON."""
    try:
        vs = get_vector_store()
        result = vs.get_all_documents()

        chunks = []
        for doc_id, doc, meta in zip(
            result['ids'][0],
            result['documents'][0],
            result['metadatas'][0]
        ):
            chunks.append({
                'id': doc_id,
                'document': doc,
                'metadata': meta
            })

        # Create JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"db_export_{timestamp}.json"
        filepath = Path("/tmp") / filename

        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(chunks, jsonfile, ensure_ascii=False, indent=2)

        return send_file(str(filepath), as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("Database Inspector Starting")
    print("="*70)
    print("\nAccess the inspector at: http://localhost:5001/")
    print("\nPress Ctrl+C to stop\n")

    app.run(host='0.0.0.0', port=5001, debug=True)


if __name__ == "__main__":
    main()
