/**
 * API Route principal para análisis de video
 * Vercel Serverless Function con Superpowers
 */

import { spawn } from 'child_process';
import path from 'path';

export const config = {
  maxDuration: 300, // 5 minutos máximo
  memory: 3008,
};

/**
 * Ejecuta el procesador de Python
 */
function runPythonProcessor(youtubeUrl) {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(process.cwd(), 'python', 'video_processor.py');
    
    // Ejecutar Python con Superpowers
    const process = spawn('python3', [pythonScript, youtubeUrl], {
      env: {
        ...process.env,
        PYTHONUNBUFFERED: '1',
        OPENCV_VIDEOIO_PRIORITY_MSMF: '0',
      },
    });

    let stdout = '';
    let stderr = '';

    process.stdout.on('data', (data) => {
      stdout += data.toString();
      console.log(`[Python] ${data.toString()}`);
    });

    process.stderr.on('data', (data) => {
      stderr += data.toString();
      console.error(`[Python Error] ${data.toString()}`);
    });

    process.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python process exited with code ${code}\n${stderr}`));
      } else {
        try {
          // El script retorna JSON
          const result = JSON.parse(stdout);
          resolve(result);
        } catch (e) {
          reject(new Error(`Failed to parse Python output: ${e.message}\n${stdout}`));
        }
      }
    });

    process.on('error', (error) => {
      reject(error);
    });
  });
}

/**
 * Handler principal
 */
export default async function handler(req, res) {
  // Solo POST permitido
  if (req.method !== 'POST') {
    return res.status(405).json({ 
      error: 'Method not allowed',
      allowed: ['POST'] 
    });
  }

  try {
    const { youtube_url } = req.body;

    // Validar URL
    if (!youtube_url) {
      return res.status(400).json({ 
        error: 'Missing youtube_url parameter' 
      });
    }

    // Validar formato de URL de YouTube
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)[\w-]+/;
    if (!youtubeRegex.test(youtube_url)) {
      return res.status(400).json({ 
        error: 'Invalid YouTube URL format' 
      });
    }

    console.log(`🎯 Processing video: ${youtube_url}`);

    // Ejecutar procesamiento
    const result = await runPythonProcessor(youtube_url);

    // Retornar resultado
    return res.status(200).json({
      success: true,
      data: result,
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error('❌ Error processing video:', error);

    return res.status(500).json({
      success: false,
      error: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined,
    });
  }
}
