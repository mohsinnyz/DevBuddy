import { useState } from 'react';
import axios from 'axios';

export default function Home() {
  const [repoUrl, setRepoUrl] = useState('');
  const [ingesting, setIngesting] = useState(false);
  const [ingestStatus, setIngestStatus] = useState<string|null>(null);
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState<{role: string, content: string}[]>([]);
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
    <main className="min-h-screen flex flex-col items-center justify-center p-4 bg-gradient-to-b from-gray-50 to-blue-50">
      <div className="w-full max-w-xl bg-white rounded-xl shadow-lg p-8 space-y-6">
        <h1 className="text-3xl font-bold text-center mb-2">DevBuddy</h1>
        <p className="text-center text-gray-600 mb-4">Paste a GitHub repo URL to analyze and chat with your codebase!</p>
        <div className="flex gap-2">
          <input
            className="flex-1 border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
            type="url"
            placeholder="https://github.com/user/repo"
            value={repoUrl}
            onChange={e => setRepoUrl(e.target.value)}
            disabled={ingesting}
          />
          <button
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            onClick={handleIngest}
            disabled={ingesting || !repoUrl}
          >
            {ingesting ? 'Ingesting...' : 'Ingest'}
          </button>
        </div>
        {ingestStatus && (
          <div className="text-center text-blue-700 font-medium mt-2">{ingestStatus}</div>
        )}
        <div className="mt-8">
          <div className="h-72 overflow-y-auto border rounded-lg bg-gray-50 p-4 flex flex-col gap-2">
            {chatHistory.length === 0 && (
              <div className="text-gray-400 text-center">No conversation yet. Ask about the repo!</div>
            )}
            {chatHistory.map((msg, idx) => (
              <div key={idx} className={msg.role === 'user' ? 'text-right' : 'text-left'}>
                <span className={msg.role === 'user' ? 'bg-blue-100 px-3 py-1 rounded-lg inline-block' : 'bg-gray-200 px-3 py-1 rounded-lg inline-block'}>
                  <b>{msg.role === 'user' ? 'You' : 'DevBuddy'}:</b> {msg.content}
                </span>
              </div>
            ))}
            {botLoading && <div className="text-center text-blue-400">DevBuddy is thinking...</div>}
          </div>
          <form
            className="flex gap-2 mt-4"
            onSubmit={e => { e.preventDefault(); handleChat(); }}
          >
            <input
              className="flex-1 border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
              type="text"
              placeholder="Ask a question about the codebase..."
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
  );
}
