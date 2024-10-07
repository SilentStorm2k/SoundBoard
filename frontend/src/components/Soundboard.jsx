// components/Soundboard.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import YouTube from 'react-youtube';

function Soundboard({ setIsAuthenticated }) {
  const [sounds, setSounds] = useState([]);
  // const [file, setFile] = useState(null);
  const [soundUrl, setSoundUrl] = useState('');
  const [soundName, setSoundName] = useState('');
  const [player, setPlayer] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchSounds();
  }, []);

  const fetchSounds = async () => {
    try {
      const response = await fetch('http://localhost:8000/sounds/', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      if (response.ok) {
        const data = await response.json();
        setSounds(data);
      } else {
        throw new Error('Failed to fetch sounds');
      }
    } catch (error) {
      console.error('Error fetching sounds:', error);
    }
  };

  const handleSoundUrlChange = (e) => {
    setSoundUrl(e.target.value);
  };

  const handleSoundNameChange = (e) => {
    setSoundName(e.target.value);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!soundUrl || !soundName) return;

    try {
      const response = await fetch('http://localhost:8000/upload-sound/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}` 
        },
        body: JSON.stringify({
          sound_url: soundUrl,
          sound_name: soundName
        })
      });
      if (response.ok) {
        alert('Sound uploaded successfully');
        fetchSounds();
        setSoundUrl('');
        setSoundName('');
      } else {
        throw new Error('Failed to upload sound');
      }
    } catch (error) {
      console.error('Error uploading sound:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    navigate('/login');
  };

  const playSound = (url) => {
    if (player) {
      player.loadVideoById(url);
      player.playVideo();
    }
  };

  const onReady = (event) => {
    setPlayer(event.target);
  };

  return (
    <div>
      <h2>Soundboard</h2>
      <button onClick={handleLogout}>Logout</button>
      <div>
        <h3>Upload Sound</h3>
        <form onSubmit={handleUpload}>
          <input 
            type="text"
            placeholder="YouTube URL"
            value={soundUrl}
            onChange={handleSoundUrlChange}
          />
          <input
            type="text"
            placeholder="Sound Name"
            value={soundName}
            onChange={handleSoundNameChange}
          />
          <button type="submit">Upload</button>
        </form>
      </div>
      <div>
        <h3>Your Sounds</h3>
        {sounds.map((sound) => (
          <button key={sound.id} onClick={() => playSound(getSoundId(sound.sound_url))}>
            {sound.sound_name}
          </button>
        ))}
      </div>
      {/* Hiding youtube video playback */}
      <YouTube
        videoId=""
        opts={{ height: '0', width: '0', playerVars: { autoplay: 1 } }}
        onReady={onReady}
      />
    </div>
  );
}

function getSoundId(url) {
  const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
  const match = url.match(regExp);
  return (match && match[2].length === 11) ? match[2] : null;
}

export default Soundboard;