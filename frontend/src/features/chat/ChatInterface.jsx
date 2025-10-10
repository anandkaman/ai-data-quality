import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { Send, Trash2, Copy, Plus, MessageSquare, User, Bot, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import axios from 'axios';

const ChatInterface = () => {
  const [chats, setChats] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState('');
  const [copiedId, setCopiedId] = useState(null);
  const [editingChatId, setEditingChatId] = useState(null);
  const [editingName, setEditingName] = useState('');
  const [initializing, setInitializing] = useState(true);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const API_BASE = 'http://localhost:8000/api/v1/chat';
  const getHeaders = useCallback(() => ({
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }), []);

  const scrollToBottom = useCallback(() => {
    requestAnimationFrame(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
    });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage, scrollToBottom]);

  useEffect(() => {
    loadChatSessions();
  }, []);

  useEffect(() => {
    if (activeChat) {
      loadChatMessages(activeChat);
    }
  }, [activeChat]);

  const loadChatSessions = async () => {
    try {
      const response = await axios.get(`${API_BASE}/sessions`, { headers: getHeaders() });
      
      if (response.data.length === 0) {
        // Create first empty chat
        await createEmptyChat();
      } else {
        setChats(response.data);
        if (!activeChat) {
          setActiveChat(response.data[0].id);
        }
      }
    } catch (error) {
      console.error('Failed to load chat sessions:', error);
    } finally {
      setInitializing(false);
    }
  };

  const createEmptyChat = async () => {
    try {
      const response = await axios.post(
        `${API_BASE}/sessions/create`,
        {},
        { headers: getHeaders() }
      );
      
      setChats([response.data]);
      setActiveChat(response.data.id);
      setMessages([]);
      
      setTimeout(() => inputRef.current?.focus(), 100);
      
    } catch (error) {
      console.error('Failed to create chat:', error);
    }
  };

  const loadChatMessages = async (sessionId) => {
    try {
      const response = await axios.get(`${API_BASE}/sessions/${sessionId}/messages`, { 
        headers: getHeaders() 
      });
      setMessages(response.data);
      setStreamingMessage('');
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  };

  const addNewChat = async () => {
    try {
      const response = await axios.post(
        `${API_BASE}/sessions/create`,
        {},
        { headers: getHeaders() }
      );
      
      await loadChatSessions();
      setActiveChat(response.data.id);
      setMessages([]);
      setStreamingMessage('');
      
      setTimeout(() => inputRef.current?.focus(), 100);
      
    } catch (error) {
      console.error('Failed to create chat:', error);
    }
  };

  const deleteChat = async (chatId) => {
    if (chats.length === 1) return;
    
    try {
      await axios.delete(`${API_BASE}/sessions/${chatId}`, { headers: getHeaders() });
      
      const newChats = chats.filter(c => c.id !== chatId);
      setChats(newChats);
      
      if (activeChat === chatId && newChats.length > 0) {
        setActiveChat(newChats[0].id);
      }
    } catch (error) {
      console.error('Failed to delete chat:', error);
    }
  };

  const deleteMessage = async (messageId) => {
    if (window.confirm('Delete this message?')) {
      setMessages(prev => prev.filter(msg => msg.id !== messageId));
    }
  };

  const renameChat = async (chatId, newName) => {
    try {
      await axios.put(
        `${API_BASE}/sessions/${chatId}/rename`,
        null,
        { 
          params: { name: newName },
          headers: getHeaders() 
        }
      );
      await loadChatSessions();
      setEditingChatId(null);
    } catch (error) {
      console.error('Failed to rename chat:', error);
    }
  };

  const sendMessageWithStreaming = async () => {
    if (!input.trim() || loading) return;

    const messageText = input;
    setInput('');
    setLoading(true);
    setStreamingMessage('');

    // Add user message optimistically
    const tempUserMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: messageText,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMessage]);

    try {
      const token = localStorage.getItem('token');
      const eventSource = new EventSource(
        `${API_BASE}/stream?chat_session_id=${activeChat || ''}&message=${encodeURIComponent(messageText)}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      let sessionId = activeChat;
      let accumulatedText = '';

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'session_id') {
            sessionId = data.session_id;
            if (!activeChat) {
              setActiveChat(sessionId);
              loadChatSessions();
            }
          } else if (data.type === 'chunk') {
            accumulatedText += data.content;
            setStreamingMessage(accumulatedText);
          } else if (data.type === 'done') {
            // Replace streaming message with actual saved message
            setStreamingMessage('');
            loadChatMessages(sessionId);
            setLoading(false);
            eventSource.close();
            
            setTimeout(() => inputRef.current?.focus(), 100);
          } else if (data.type === 'error') {
            console.error('Streaming error:', data.error);
            setStreamingMessage('');
            setLoading(false);
            eventSource.close();
          }
        } catch (error) {
          console.error('Parse error:', error);
        }
      };

      eventSource.onerror = (error) => {
        console.error('EventSource error:', error);
        setStreamingMessage('');
        setLoading(false);
        eventSource.close();
        
        // Fallback to regular API
        sendMessageRegular(messageText, sessionId);
      };

    } catch (error) {
      console.error('Streaming failed:', error);
      setLoading(false);
      
      // Fallback to regular API
      sendMessageRegular(messageText, activeChat);
    }
  };

  const sendMessageRegular = async (messageText, sessionId) => {
    try {
      const response = await axios.post(
        API_BASE,
        {
          chat_session_id: sessionId,
          message: messageText,
          system_prompt: "You are a helpful AI assistant specializing in data quality and data science. Use markdown formatting."
        },
        { headers: getHeaders() }
      );

      await loadChatMessages(sessionId || response.data.chat_session_id);
      
      if (!sessionId) {
        setActiveChat(response.data.chat_session_id);
        await loadChatSessions();
      }
      
      setTimeout(() => inputRef.current?.focus(), 100);
      
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyMessage = useCallback((content, id) => {
    navigator.clipboard.writeText(content);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  }, []);

  const startEditing = (chat) => {
    setEditingChatId(chat.id);
    setEditingName(chat.name);
  };

  const finishEditing = (chatId) => {
    if (editingName.trim()) {
      renameChat(chatId, editingName);
    } else {
      setEditingChatId(null);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !loading) {
      e.preventDefault();
      sendMessageWithStreaming();
    }
  };

  const markdownComponents = useMemo(() => ({
    code({node, inline, className, children, ...props}) {
      return inline ? (
        <code className="bg-gray-200 text-red-600 px-1 py-0.5 rounded text-sm font-mono" {...props}>
          {children}
        </code>
      ) : (
        <code className="block bg-gray-800 text-green-400 p-3 rounded-md overflow-x-auto text-sm font-mono whitespace-pre" {...props}>
          {children}
        </code>
      );
    },
    p({children}) {
      return <p className="mb-2 leading-relaxed">{children}</p>;
    },
    strong({children}) {
      return <strong className="font-bold text-gray-900">{children}</strong>;
    },
    ul({children}) {
      return <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>;
    },
    ol({children}) {
      return <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>;
    },
    li({children}) {
      return <li className="ml-2">{children}</li>;
    },
    a({href, children}) {
      return <a href={href} className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">{children}</a>;
    }
  }), []);

  if (initializing) {
    return (
      <div className="flex h-[calc(100vh-16rem)] items-center justify-center bg-white rounded-lg shadow-md">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Initializing chat...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-16rem)] gap-4">
      {/* Sidebar */}
      <div className="w-64 bg-white rounded-lg shadow-md p-4 flex flex-col">
        <button
          onClick={addNewChat}
          className="btn btn-primary mb-4 flex items-center justify-center space-x-2 hover:scale-105 transition-transform"
        >
          <Plus className="w-4 h-4" />
          <span>New Chat</span>
        </button>

        <div className="flex-1 overflow-y-auto space-y-2 scrollbar-thin scrollbar-thumb-gray-300">
          {chats.map(chat => (
            <div
              key={chat.id}
              className={`flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all ${
                activeChat === chat.id
                  ? 'bg-primary-50 border border-primary-200 shadow-sm'
                  : 'hover:bg-gray-50 border border-transparent'
              }`}
              onClick={() => setActiveChat(chat.id)}
            >
              <div className="flex items-center space-x-2 flex-1 min-w-0">
                <MessageSquare className="w-4 h-4 flex-shrink-0 text-gray-600" />
                {editingChatId === chat.id ? (
                  <input
                    type="text"
                    value={editingName}
                    onChange={(e) => setEditingName(e.target.value)}
                    onBlur={() => finishEditing(chat.id)}
                    onKeyPress={(e) => e.key === 'Enter' && finishEditing(chat.id)}
                    className="text-sm flex-1 px-2 py-1 border rounded focus:outline-none focus:ring-1 focus:ring-primary-500"
                    autoFocus
                    onClick={(e) => e.stopPropagation()}
                  />
                ) : (
                  <span className="text-sm truncate">{chat.name}</span>
                )}
              </div>
              <div className="flex items-center space-x-1">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    startEditing(chat);
                  }}
                  className="p-1 hover:bg-blue-100 rounded transition-colors"
                  title="Rename"
                >
                  <svg className="w-3 h-3 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                  </svg>
                </button>
                {chats.length > 1 && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteChat(chat.id);
                    }}
                    className="p-1 hover:bg-red-100 rounded transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="w-3 h-3 text-red-600" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Chat area */}
      <div className="flex-1 bg-white rounded-lg shadow-md flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-4 scrollbar-thin scrollbar-thumb-gray-300">
          {messages.length === 0 && !streamingMessage ? (
            <div className="h-full flex items-center justify-center text-gray-400">
              <div className="text-center">
                <Bot className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <p className="text-lg">Start a conversation with Gemma 2:2b</p>
                <p className="text-sm mt-2">Ask anything about data quality or data science</p>
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} group`}
                >
                  <div className={`flex space-x-3 max-w-3xl ${msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      msg.role === 'user' ? 'bg-primary-600' : 'bg-gray-600'
                    }`}>
                      {msg.role === 'user' ? <User className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-white" />}
                    </div>
                    
                    <div className={`flex-1 p-4 rounded-lg shadow-sm ${
                      msg.role === 'user' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-900'
                    }`}>
                      {msg.role === 'user' ? (
                        <p className="whitespace-pre-wrap break-words">{msg.content}</p>
                      ) : (
                        <div className="prose prose-sm max-w-none">
                          <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                            {msg.content}
                          </ReactMarkdown>
                        </div>
                      )}
                      
                      <div className="flex items-center space-x-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button onClick={() => copyMessage(msg.content, msg.id)} className={`p-1 rounded hover:bg-opacity-20 hover:bg-gray-500 ${msg.role === 'user' ? 'text-white' : 'text-gray-600'}`} title="Copy">
                          {copiedId === msg.id ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                        </button>
                        <button onClick={() => deleteMessage(msg.id)} className={`p-1 rounded hover:bg-opacity-20 hover:bg-red-500 ${msg.role === 'user' ? 'text-white' : 'text-gray-600'}`} title="Delete">
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {streamingMessage && (
                <div className="flex justify-start">
                  <div className="flex space-x-3 max-w-3xl">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1 p-4 rounded-lg bg-gray-100 shadow-sm">
                      <div className="prose prose-sm max-w-none">
                        <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                          {streamingMessage}
                        </ReactMarkdown>
                      </div>
                      <div className="inline-block w-2 h-4 bg-gray-600 animate-pulse ml-1"></div>
                    </div>
                  </div>
                </div>
              )}
              
              {loading && !streamingMessage && (
                <div className="flex justify-start">
                  <div className="flex space-x-3 max-w-3xl">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1 p-4 rounded-lg bg-gray-100 shadow-sm">
                      <div className="flex space-x-2">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div className="border-t p-4 bg-gray-50">
          <div className="flex space-x-2">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about data quality, anomalies, or data science..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              disabled={loading}
              autoFocus
            />
            <button
              onClick={sendMessageWithStreaming}
              disabled={loading || !input.trim()}
              className="btn btn-primary px-6 flex items-center space-x-2 hover:scale-105 transition-transform disabled:hover:scale-100"
            >
              <Send className="w-4 h-4" />
              <span>Send</span>
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
