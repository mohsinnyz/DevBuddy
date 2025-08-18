// D:\DevBuddy\frontend\src\pages\index.tsx

import { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

import Header from '../components/Header';
import Footer from '../components/Footer';

export default function Home() {
  const [repoUrl, setRepoUrl] = useState('');
  const [ingesting, setIngesting] = useState(false);
  const [ingestStatus, setIngestStatus] = useState<string | null>(null);
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState<{ role: string, content: string }[]>([]);
  const [botLoading, setBotLoading] = useState(false);

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000/api';

  const handleIngest = async () => {
    setIngesting(true);
    setIngestStatus('Ingesting repository...');
    try {
      const res = await axios.post(`${backendUrl}/ingest`, { repo_url: repoUrl });
      setIngestStatus(res.data.message);
    } catch (err: any) {
      setIngestStatus('Error: ' + (err?.response?.data?.detail || err.message));
    }
    setIngesting(false);
  };

  const handleChat = async () => {
    if (!chatInput.trim()) return;
    setBotLoading(true);
    setChatHistory([...chatHistory, { role: 'user', content: chatInput }]);
    try {
      const res = await axios.post(`${backendUrl}/chat`, {
        message: chatInput,
        repo_url: repoUrl,
        conversation_history: chatHistory,
      });
      setChatHistory([...chatHistory, { role: 'user', content: chatInput }, { role: 'assistant', content: res.data.response }]);
    } catch (err: any) {
      setChatHistory([...chatHistory, { role: 'user', content: chatInput }, { role: 'assistant', content: 'Error: ' + (err?.response?.data?.detail || err.message) }]);
    }
    setChatInput('');
    setBotLoading(false);
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-1 flex flex-col items-center justify-center p-4 bg-gradient-to-br from-gray-900 to-sky-900">
        <div className="w-full max-w-5xl bg-gray-900 rounded-xl shadow-lg shadow-black p-8 space-y-6">
          <h1 className="text-3xl font-bold text-center mb-2 text-white">DevBuddy</h1>
          <p className="text-center text-white mb-4">Paste a GitHub repo URL to analyze and chat with your that one Developer Buddy!</p>
          <div className="flex gap-2">
            <input
              className="flex-1 border-gray-700 bg-gray-800 text-white rounded-lg px-8 py-2 focus:outline-none focus:ring-2 focus:ring-sky-400 placeholder-gray-500"
              type="url"
              placeholder="https://github.com/user/repo"
              value={repoUrl}
              onChange={e => setRepoUrl(e.target.value)}
              disabled={ingesting}
            />
            <button
              className="bg-sky-600 text-white px-4 py-2 rounded-lg hover:bg-sky-700 disabled:opacity-50"
              onClick={handleIngest}
              disabled={ingesting || !repoUrl}
            >
              {ingesting ? 'Ingesting...' : 'Ingest'}
            </button>
          </div>
          {ingestStatus && (
            <div className="text-center text-sky-400 font-medium mt-2">{ingestStatus}</div>
          )}
          <div className="mt-8">
            <div className="h-72 overflow-y-auto border border-gray-700 rounded-lg bg-gray-800 p-4 flex flex-col gap-2">
              {chatHistory.length === 0 && (
                <div className="text-gray-500 text-center">No conversation yet. Ask about the repo!</div>
              )}
              {chatHistory.map((msg, idx) => (
                <div key={idx} className={msg.role === 'user' ? 'text-right' : 'text-left'}>
                  <span className={msg.role === 'user' ? 'bg-sky-700 text-white px-3 py-1 rounded-lg inline-block' : 'bg-gray-600 text-white px-3 py-1 rounded-lg inline-block'}>
                    <b>{msg.role === 'user' ? 'You' : 'DevBuddy'}:</b>
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </span>
                </div>
              ))}
              {botLoading && <div className="text-center text-sky-400">DevBuddy is thinking...</div>}
            </div>
            <form
              className="flex gap-2 mt-4"
              onSubmit={e => { e.preventDefault(); handleChat(); }}
            >
              <input
                className="flex-1 border-gray-700 bg-gray-800 text-white rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sky-400 placeholder-gray-500"
                type="text"
                placeholder="Start Conversation Here"
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                disabled={botLoading || !repoUrl}
              />
              <button
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
                type="submit"
                disabled={botLoading || !chatInput.trim() || !repoUrl}
              >
                Send
              </button>
            </form>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}