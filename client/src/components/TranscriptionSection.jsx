/**
 * TranscriptionSection Component
 * * Displays interview transcriptions with editing and export functionality.
 * Provides a workspace for viewing and annotating transcribed text.
 */
/**
 * TranscriptionSection Component
 * Displays interview transcriptions with rich-text editing (bold/italic/highlight)
 * and simple saving (POST to API if available, else localStorage fallback).
 */
import React, { useState, useEffect, useCallback } from 'react';
import { API_ENDPOINTS } from "../config/api";
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Highlight from '@tiptap/extension-highlight';

const DEFAULT_PLACEHOLDER = `<p class="text-slate-400">Transcribed interview text will go here.</p>`;

const MenuBar = ({ editor }) => {
  if (!editor) return null;
  return (
    <div className="flex items-center gap-2 mb-2 border-b border-slate-500 pb-2">
      <button
        onClick={() => editor.chain().focus().toggleBold().run()}
        className={`p-2 rounded hover:bg-slate-600 ${editor.isActive('bold') ? 'bg-indigo-600 text-white' : 'text-slate-200'}`}
        type="button"
        title="Bold"
      >
        <i className="bi bi-type-bold"></i>
      </button>
      <button
        onClick={() => editor.chain().focus().toggleItalic().run()}
        className={`p-2 rounded hover:bg-slate-600 ${editor.isActive('italic') ? 'bg-indigo-600 text-white' : 'text-slate-200'}`}
        type="button"
        title="Italic"
      >
        <i className="bi bi-type-italic"></i>
      </button>
      <button
        onClick={() => editor.chain().focus().toggleHighlight().run()}
        className={`p-2 rounded hover:bg-slate-600 ${editor.isActive('highlight') ? 'bg-yellow-300 text-black' : 'text-slate-200'}`}
        type="button"
        title="Highlight"
      >
        <i className="bi bi-highlighter"></i>
      </button>
    </div>
  );
};

const TranscriptionSection = ({ transcriptionData, collectionName }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [vectorData, setVectorData] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const filename = transcriptionData?.filename || `${collectionName || 'vector_documents'}.html`;
  const initialHTML = transcriptionData?.transcription || '';

  const editor = useEditor({
    extensions: [StarterKit, Highlight],
    content: initialHTML || DEFAULT_PLACEHOLDER,
    editable: isEditing,
  });

  // Fetch data from vector database
  useEffect(() => {
    const fetchVectorData = async () => {
      if (!collectionName) {
        setIsLoading(false);
        return;
      }
      try {
        setIsLoading(true);
        const url = API_ENDPOINTS.DOCUMENTS_BY_COLLECTION(collectionName);
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        if (data.full_text) {
          setVectorData(data.full_text);
          // Update editor content with vector data
          if (editor) {
            editor.commands.setContent(`<p>${data.full_text}</p>`, false);
          }
        } else {
          setVectorData('No documents found in this collection.');
        }
      } catch (err) {
        console.error('Failed to fetch vector data:', err);
        setError(err.message);
        setVectorData('Failed to load documents from vector database.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchVectorData();
  }, [editor, collectionName]);

  useEffect(() => {
    if (!editor) return;
    const html = initialHTML || DEFAULT_PLACEHOLDER;
    editor.commands.setContent(html, false);
    setIsEditing(false);
  }, [initialHTML, editor]);

  useEffect(() => {
    if (editor) editor.setEditable(isEditing);
  }, [isEditing, editor]);

  const handleDownload = useCallback(() => {
    if (!editor) return;
    const html = editor.getHTML();
    const blob = new Blob([html], { type: 'text/html' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.style.display = 'none';
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(link);
  }, [editor, filename]);

  const handleSave = useCallback(async () => {
    if (!editor) return;
    const html = editor.getHTML();

    try {
      if (API_ENDPOINTS?.SAVE) {
        const resp = await fetch(API_ENDPOINTS.SAVE, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ filename, html }),
        });
        if (!resp.ok) throw new Error(await resp.text());
      } else {
        localStorage.setItem(`qualai:${filename}`, html);
      }
      setIsEditing(false);
    } catch (err) {
      console.error('Save failed:', err);
      try {
        localStorage.setItem(`qualai:${filename}`, html);
        alert('Saved locally (no API).');
      } catch {}
      setIsEditing(false);
    }
  }, [editor, filename]);

  return (
    <div className="bg-slate-800 rounded-xl shadow-md p-4 flex-1 flex flex-col">
      <div className="flex justify-between items-center mb-2 font-sora">
        <h3 className="text-lg text-white font-bold">Transcriptions</h3>
        <div className='flex gap-3'>
          <button
            className={`bg-indigo-600 text-white text-sm px-4 py-2 rounded-md flex items-center gap-2 ${isEditing ? 'opacity-50 cursor-not-allowed' : 'hover:bg-indigo-700'}`}
            aria-label="Edit transcription"
            onClick={() => setIsEditing(true)}
            disabled={isEditing}
          >
            <i className="bi bi-pencil" aria-hidden="true" />
          </button>
          <button
            className="bg-indigo-600 text-white text-sm px-4 py-2 rounded-md hover:bg-indigo-700 flex items-center gap-2"
            aria-label="Download transcription"
            onClick={handleDownload}
          >
            <i className="bi bi-download" aria-hidden="true" />
          </button>
          {isEditing && (
            <button
              className="bg-green-600 text-white text-sm px-4 py-2 rounded-md hover:bg-green-700 flex items-center gap-2"
              aria-label="Save transcription"
              onClick={handleSave}
            >
              <i className="bi bi-check-lg" aria-hidden="true" />
              Save
            </button>
          )}
        </div>
      </div>
      <div className="bg-slate-700 rounded-lg p-3 flex-1 flex flex-col min-h-0">
        {isEditing && <MenuBar editor={editor} />}
        
        {/* Loading and error states */}
        {isLoading && (
          <div className="flex items-center justify-center p-4">
            <div className="text-slate-300">Loading documents from vector database...</div>
          </div>
        )}
        
        {error && (
          <div className="bg-red-900/20 border border-red-500/50 rounded-lg p-3 mb-3">
            <div className="text-red-300 text-sm">Error: {error}</div>
          </div>
        )}
        
        {/* Vector data info */}
        {vectorData && !isLoading && (
          <div className="bg-blue-900/20 border border-blue-500/50 rounded-lg p-3 mb-3">
            <div className="text-blue-300 text-sm">
              Displaying content from vector database ({vectorData.length} characters)
            </div>
          </div>
        )}
        
        {/* Scrollable content area */}
        <div className="flex-1 overflow-y-auto min-h-0 border border-slate-600 rounded-lg bg-slate-800" style={{ maxHeight: '400px' }}>
          <div className="p-4">
            <EditorContent editor={editor} className="tiptap-editor" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default TranscriptionSection;
