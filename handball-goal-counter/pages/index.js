import { useState } from 'react';

export default function Home() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    if (!url) {
      setError('Por favor ingresa una URL de YouTube');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('/api/analyze-video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ youtube_url: url }),
      });

      const data = await response.json();

      if (data.success) {
        setResult(data.data);
      } else {
        setError(data.error || 'Error desconocido');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px',
      fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif',
    }}>
      <div style={{
        maxWidth: '700px',
        margin: '40px auto',
        background: 'white',
        borderRadius: '20px',
        padding: '40px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
      }}>
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <div style={{ fontSize: '4em', marginBottom: '10px' }}>🏐⚽</div>
          <h1 style={{ color: '#667eea', margin: '0 0 10px 0' }}>
            Handball Goal Counter
          </h1>
          <p style={{ color: '#666', margin: 0 }}>
            Detecta goles automáticamente desde videos de YouTube
          </p>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ 
            display: 'block', 
            marginBottom: '8px', 
            fontWeight: 'bold',
            color: '#333' 
          }}>
            URL de YouTube:
          </label>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.youtube.com/watch?v=..."
            style={{
              width: '100%',
              padding: '12px',
              fontSize: '16px',
              border: '2px solid #e0e0e0',
              borderRadius: '8px',
              outline: 'none',
              boxSizing: 'border-box',
            }}
          />
        </div>

        <button
          onClick={handleAnalyze}
          disabled={loading}
          style={{
            width: '100%',
            padding: '15px',
            fontSize: '16px',
            fontWeight: 'bold',
            background: loading ? '#999' : '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: 'background 0.3s',
          }}
        >
          {loading ? '⏳ Analizando video...' : '🎯 Analizar Video'}
        </button>

        {error && (
          <div style={{
            marginTop: '20px',
            padding: '15px',
            background: '#fee',
            border: '1px solid #fcc',
            borderRadius: '8px',
            color: '#c33',
          }}>
            ❌ {error}
          </div>
        )}

        {result && (
          <div style={{
            marginTop: '20px',
            padding: '20px',
            background: '#f7f9fc',
            borderRadius: '8px',
            border: '2px solid #667eea',
          }}>
            <h3 style={{ color: '#667eea', marginTop: 0 }}>
              ✅ Resultados del Análisis
            </h3>
            <div style={{ display: 'grid', gap: '10px' }}>
              <div><strong>⚽ Goles detectados:</strong> {result.goals_detected}</div>
              <div><strong>⏱️ Tiempo de procesamiento:</strong> {result.processing_time?.toFixed(2)}s</div>
              <div><strong>🎬 Frames totales:</strong> {result.total_frames}</div>
              {result.team_scores && (
                <div>
                  <strong>📊 Puntajes:</strong>
                  <ul>
                    <li>Equipo A: {result.team_scores.team_a}</li>
                    <li>Equipo B: {result.team_scores.team_b}</li>
                  </ul>
                </div>
              )}
              {result.goal_timestamps && result.goal_timestamps.length > 0 && (
                <div>
                  <strong>🕒 Timestamps de goles:</strong>
                  <div style={{ marginTop: '5px' }}>
                    {result.goal_timestamps.map((ts, i) => (
                      <span key={i} style={{
                        display: 'inline-block',
                        margin: '2px',
                        padding: '4px 8px',
                        background: '#667eea',
                        color: 'white',
                        borderRadius: '4px',
                        fontSize: '14px',
                      }}>
                        {ts.toFixed(1)}s
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        <div style={{
          marginTop: '30px',
          padding: '15px',
          background: '#f0f4ff',
          borderRadius: '8px',
          fontSize: '14px',
          color: '#666',
        }}>
          <strong>🔧 API Endpoint:</strong> <code>POST /api/analyze-video</code>
        </div>
      </div>
    </div>
  );
}
